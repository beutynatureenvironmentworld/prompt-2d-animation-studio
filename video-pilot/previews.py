"""One-shot motion previews with an atomic visitor and pilot allowance."""
import hashlib
import ipaddress
import os
import secrets
import shutil
import subprocess
import time

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend import BASE, DATA, RATIOS, STYLES, db, now

router = APIRouter()
folder = DATA / "previews"
folder.mkdir(mode=0o700, exist_ok=True)
with db() as con:
    con.execute("""CREATE TABLE IF NOT EXISTS previews (
        id TEXT PRIMARY KEY, visitor TEXT, network TEXT, created INTEGER,
        state TEXT, prompt TEXT, ratio TEXT, seed INTEGER)""")
    con.execute("CREATE INDEX IF NOT EXISTS preview_age ON previews(created)")
    con.execute("CREATE TABLE IF NOT EXISTS preview_budget (id INTEGER PRIMARY KEY, used INTEGER, salt TEXT)")
    con.execute("INSERT OR IGNORE INTO preview_budget VALUES (1,0,?)", (secrets.token_hex(32),))


class Spec(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    style: str
    ratio: str


def failure(status, message, wait=None):
    raise HTTPException(status, message, headers={"Retry-After": str(wait)} if wait else None)


@router.get("/api/preview-availability")
def availability():
    with db() as con:
        used = con.execute("SELECT used FROM preview_budget WHERE id=1").fetchone()[0]
    return JSONResponse({"available": used < int(os.getenv("PREVIEW_TOTAL_CALLS", "0")),
                         "demo": (DATA/"preview-demo"/"frame.jpg").is_file()},
                        headers={"Cache-Control":"no-store"})


@router.get("/api/preview-demo/{asset}")
def demo(asset: str):
    if asset not in {"motion.mp4", "frame.jpg"} or not (DATA/"preview-demo"/asset).is_file():
        failure(404, "Studio sample unavailable.")
    return FileResponse(DATA/"preview-demo"/asset, headers={"Cache-Control":"public, max-age=86400"})


@router.post("/api/previews")
def create(spec: Spec, request: Request):
    if request.headers.get("origin") != BASE:
        failure(403, "Please use the preview button in the studio.")
    if spec.style not in STYLES or spec.ratio not in RATIOS or not spec.prompt.strip():
        failure(422, "Enter a scene and select a supported style and aspect ratio.")
    try:
        address = ipaddress.ip_address(request.headers.get("cf-connecting-ip", ""))
    except ValueError:
        failure(503, "The preview connection is unavailable.")
    network = str(ipaddress.ip_network((address, 64 if address.version == 6 else 32), strict=False))
    visitor = request.cookies.get("preview_visitor", "")
    if len(visitor) != 48 or any(c not in "0123456789abcdef" for c in visitor):
        visitor = secrets.token_hex(24)
    stamp = now()
    with db() as con:
        con.execute("BEGIN IMMEDIATE")
        budget = con.execute("SELECT * FROM preview_budget WHERE id=1").fetchone()
        def digest(value):
            return hashlib.blake2b(value.encode(), key=bytes.fromhex(budget["salt"]), digest_size=20).hexdigest()
        identity, subnet = digest(visitor), digest(network)
        attempts = con.execute("""SELECT created FROM previews WHERE created>? AND
            (visitor=? OR network=?) ORDER BY created""", (stamp-3600, identity, subnet)).fetchall()
        if len(attempts) >= 3:
            failure(429, "Hourly preview limit reached.", attempts[0][0]+3600-stamp)
        if budget["used"] >= int(os.getenv("PREVIEW_TOTAL_CALLS", "0")):
            failure(503, "Free motion previews are currently unavailable.")
        if con.execute("SELECT 1 FROM previews WHERE state IN ('queued','rendering')").fetchone():
            failure(503, "The preview GPU is busy. Try again shortly.", 30)
        token = secrets.token_urlsafe(24)
        con.execute("INSERT INTO previews VALUES(?,?,?,?,?,?,?,?)",
                    (token,identity,subnet,stamp,"queued",STYLES[spec.style]+". "+spec.prompt.strip(),
                     spec.ratio,secrets.randbits(32)))
        con.execute("UPDATE preview_budget SET used=used+1 WHERE id=1")
    response = JSONResponse({"id": token, "remaining": 2-len(attempts)}, status_code=202,
                            headers={"Cache-Control":"no-store"})
    response.set_cookie("preview_visitor",visitor,max_age=86400,httponly=True,secure=True,samesite="strict")
    return response


def lookup(token):
    with db() as con:
        row = con.execute("SELECT state FROM previews WHERE id=? AND created>?",(token,now()-3600)).fetchone()
    if not row:
        failure(404, "This preview has expired.")
    return row["state"]


@router.get("/api/previews/{token}")
def status(token: str):
    return JSONResponse({"state":lookup(token)}, headers={"Cache-Control":"no-store"})


@router.get("/api/previews/{token}/{asset}")
def media(token: str, asset: str):
    if lookup(token) != "ready" or asset not in {"motion.mp4","frame.jpg"}:
        failure(404, "Preview unavailable.")
    return FileResponse(folder/token/asset, headers={"Cache-Control":"private, no-store"})


def work():
    import modal
    with db() as con:
        con.execute("UPDATE previews SET state='failed',prompt='' WHERE state='rendering'")
    while True:
        with db() as con:
            con.execute("BEGIN IMMEDIATE")
            for old in con.execute("SELECT id FROM previews WHERE created<=?",(now()-3600,)):
                shutil.rmtree(folder/old[0], ignore_errors=True)
            con.execute("DELETE FROM previews WHERE created<=?",(now()-3600,))
            job = con.execute("SELECT * FROM previews WHERE state='queued' ORDER BY created LIMIT 1").fetchone()
            if job:
                con.execute("UPDATE previews SET state='rendering',prompt='' WHERE id=?",(job["id"],))
        if not job:
            time.sleep(8)
            continue
        out = folder/job["id"]
        try:
            out.mkdir()
            render = modal.Function.from_name("vidbest-ltx25","render_shot")
            data = render.remote(job["prompt"],job["ratio"],1,job["seed"])
            (out/"motion.mp4").write_bytes(data)
            subprocess.run(["ffmpeg","-v","error","-ss","0.5","-i",str(out/"motion.mp4"),
                            "-frames:v","1",str(out/"frame.jpg")],check=True,timeout=30)
            if not (out/"frame.jpg").stat().st_size:
                raise ValueError("Empty frame")
            state = "ready"
        except Exception as error:
            print("Preview failed:", type(error).__name__, flush=True)
            shutil.rmtree(out,ignore_errors=True)
            state = "failed"
        with db() as con:
            con.execute("UPDATE previews SET state=? WHERE id=?",(state,job["id"]))


if __name__ == "__main__":
    work()
