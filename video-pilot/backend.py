"""Single-host video pilot. Run uvicorn backend:app and python backend.py worker."""
import contextlib
import email.message
import fcntl
import hashlib
import hmac
import html
import json
import math
import os
import secrets
import shutil
import smtplib
import sqlite3
import ssl
import subprocess
import sys
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(docs_url=None, redoc_url=None)
DATA = Path(os.getenv("VIDEO_DATA", "./private-video-data")).resolve()
DATA.mkdir(mode=0o700, parents=True, exist_ok=True)
BASE = os.getenv("BASE_URL", "https://ai.vid.best").rstrip("/")
RATIOS = {"16:9", "9:16", "1:1"}
SHOT = 5
LIMIT = 3 * 3600
STYLES = {"2D": "hand-drawn 2D animation", "2.5D": "layered 2.5D animation with parallax", "3D": "cinematic 3D animation",
          "Cinematic": "cinematic filmmaking, expressive lighting and purposeful camera movement",
          "Presenter": "on-camera presenter addressing the audience, medium shot and natural gestures",
          "Avatar": "expressive digital avatar, character-focused framing and natural movement"}


@contextlib.contextmanager
def db():
    con = sqlite3.connect(DATA / "orders.sqlite3", timeout=15)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()


with db() as con:
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("BEGIN IMMEDIATE")
    con.execute("""CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY, token TEXT UNIQUE, email TEXT, prompt TEXT, style TEXT,
        ratio TEXT, seconds INTEGER, amount INTEGER, gpu INTEGER, eta INTEGER,
        created INTEGER, paid INTEGER, payment_id TEXT UNIQUE, state TEXT,
        mail_at INTEGER DEFAULT 0, next_mail INTEGER DEFAULT 0)""")
    con.execute("""CREATE TABLE IF NOT EXISTS runtime (id INTEGER PRIMARY KEY, beat INTEGER)""")

    columns = {col[1] for col in con.execute("PRAGMA table_info(orders)")}
    for name, definition in [("currency","TEXT DEFAULT 'LKR'"), ("download_at","INTEGER"),
                             ("backup_sha","TEXT"), ("retry_backup","INTEGER DEFAULT 0")]:
        if name not in columns:
            con.execute(f"ALTER TABLE orders ADD COLUMN {name} {definition}")


def now():
    return int(time.time())


def offer(paid_seconds):
    bonus = paid_seconds // 10 if paid_seconds in (60, 300, 600) else 0
    # Prorate 46 US cents per minute, rounding to the nearest cent.
    cents = max(1, (paid_seconds * 46 + 30) // 60)
    return paid_seconds + bonus, cents


def estimate(delivered_seconds):
    gpu = math.ceil(delivered_seconds / SHOT) * int(os.getenv("SHOT_GPU_SECONDS", "45"))
    if gpu <= 0:
        raise RuntimeError("invalid render estimate")
    return gpu, gpu + int(os.getenv("ORDER_BUFFER_SECONDS", "240"))


def availability(con, seconds, gpu, eta):
    required = ["PAYHERE_MERCHANT_ID", "PAYHERE_MERCHANT_SECRET", "SMTP_HOST", "SMTP_FROM",
                "SHOT_GPU_SECONDS", "FREE_GPU_SECONDS", "BUDGET_START_UNIX",
                "BENCHMARK_MAX_SECONDS", "MODAL_APP", "MODAL_FUNCTION"]
    if os.getenv("CHECKOUT_ENABLED") != "1" or any(not os.getenv(k) for k in required):
        return "Checkout opens after the payment and render pilot is verified."
    if seconds > int(os.environ["BENCHMARK_MAX_SECONDS"]):
        return "This duration is awaiting a successful render benchmark."
    if not con.execute("SELECT 1 FROM runtime WHERE id=1 AND beat>?", (now()-120,)).fetchone():
        return "The render worker is offline."
    pending = con.execute("""SELECT COALESCE(SUM(eta),0) FROM orders WHERE state IN ('queued','rendering')
                 OR (state='awaiting' AND created>?)""", (now()-600,)).fetchone()[0]
    if pending + eta > LIMIT - 600:
        return "No render slot is available within three hours."
    used = con.execute("""SELECT COALESCE(SUM(gpu),0) FROM orders WHERE
          (paid>=? OR (state='awaiting' AND created>?))""",
          (int(os.environ["BUDGET_START_UNIX"]), now()-600)).fetchone()[0]
    if used + gpu > int(os.environ["FREE_GPU_SECONDS"]):
        return "The pilot GPU allowance is fully reserved."
    return ""


def validate_spec(seconds, ratio):
    if not 1 <= seconds <= 1800 or ratio not in RATIOS:
        raise HTTPException(422, "Choose 1–1800 seconds and a supported aspect ratio.")


@app.get("/api/quote")
def quote(seconds: int, ratio: str):
    validate_spec(seconds, ratio)
    delivered, price = offer(seconds)
    gpu, eta = estimate(delivered)
    with db() as con:
        reason = availability(con, delivered, gpu, eta)
    return dict(amount_usd=price/100, bonus_seconds=delivered-seconds, delivered_seconds=delivered, available=not reason, reason=reason, estimated_minutes=math.ceil(eta/60))


class Order(BaseModel):
    email: str = Field(min_length=3, max_length=254, pattern=r"^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$")
    prompt: str = Field(min_length=1, max_length=3000)
    style: str
    ratio: str
    seconds: int = Field(strict=True, ge=1, le=1800)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=5, max_length=30)
    address: str = Field(min_length=1, max_length=250)
    city: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)


def md5(s):
    return hashlib.md5(s.encode(), usedforsecurity=False).hexdigest().upper()


def signature(*fields):
    return md5("".join(fields) + md5(os.environ["PAYHERE_MERCHANT_SECRET"]))


@app.post("/api/checkout")
def checkout(order: Order):
    validate_spec(order.seconds, order.ratio)
    if order.style not in STYLES or not order.prompt.strip():
        raise HTTPException(422, "Enter a prompt and select an animation style.")
    delivered, price = offer(order.seconds)
    gpu, eta = estimate(delivered)
    oid, token = secrets.token_hex(12), secrets.token_urlsafe(32)
    with db() as con:
        con.execute("BEGIN IMMEDIATE")
        reason = availability(con, delivered, gpu, eta)
        if reason:
            raise HTTPException(409, reason)
        con.execute("""INSERT INTO orders(id,token,email,prompt,style,ratio,seconds,amount,gpu,eta,created,state,currency)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,'awaiting','USD')""",
                    (oid,token,order.email,order.prompt.strip(),order.style,order.ratio,delivered,price,gpu,eta,now()))
    merchant, amount = os.environ["PAYHERE_MERCHANT_ID"], f"{price//100}.{price%100:02d}"
    fields = order.model_dump(include={"first_name","last_name","email","phone","address","city","country"})
    status = BASE + "/api/status/" + token
    fields.update(merchant_id=merchant, order_id=oid, items=f"{delivered}s video ({order.seconds}s paid)",
                  currency="USD", amount=amount, hash=signature(merchant,oid,amount,"USD"),
                  return_url=status, cancel_url=status, notify_url=BASE+"/api/payhere")
    host = "www" if os.getenv("PAYHERE_LIVE") == "1" else "sandbox"
    return dict(url=f"https://{host}.payhere.lk/pay/checkout", fields=fields)


@app.post("/api/payhere")
async def payhere(request: Request):
    if not os.getenv("PAYHERE_MERCHANT_SECRET"):
        raise HTTPException(503)
    body = bytearray()
    async for piece in request.stream():
        body.extend(piece)
        if len(body) > 16384:
            raise HTTPException(413)
    try:
        data = {k:v[0] for k,v in parse_qs(body.decode(), max_num_fields=60).items() if len(v)==1}
        merchant, oid, amount, currency, state = [data[k] for k in
            ("merchant_id","order_id","payhere_amount","payhere_currency","status_code")]
        valid = hmac.compare_digest(data["md5sig"], signature(merchant,oid,amount,currency,state))
        value = Decimal(amount)
    except (ValueError,KeyError,TypeError,InvalidOperation):
        raise HTTPException(400)
    if not valid or merchant != os.getenv("PAYHERE_MERCHANT_ID") or currency not in ("LKR","USD") or not value.is_finite():
        raise HTTPException(403)
    with db() as con:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT * FROM orders WHERE id=?",(oid,)).fetchone()
        if not row or currency != row["currency"] or value * (100 if currency == "USD" else 1) != row["amount"]:
            raise HTTPException(409)
        if state == "2":
            payment = data.get("payment_id")
            if not payment:
                raise HTTPException(400)
            if row["payment_id"] and row["payment_id"] != payment:
                raise HTTPException(409)
            if row["state"] == "awaiting":
                status = "queued" if row["created"]+600 >= now() else "refund_review"
                con.execute("UPDATE orders SET state=?,paid=?,payment_id=? WHERE id=?",
                            (status,now(),payment,oid))
        elif state == "-3":
            con.execute("UPDATE orders SET state='charged_back' WHERE id=?", (oid,))
    return {"received": True}


@app.get("/api/status/{token}")
def status(token: str):
    with db() as con:
        row = con.execute("SELECT state,created FROM orders WHERE token=?", (token,)).fetchone()
    if not row:
        raise HTTPException(404)
    state = row["state"]
    label = {"awaiting":"Waiting for payment confirmation", "queued":"Payment received · queued",
             "rendering":"Rendering your video", "ready":"Your video is ready",
             "refund_review":"Delivery interrupted · payment under refund review",
             "charged_back":"Payment reversed"}.get(state,state)
    if state == "awaiting" and row["created"]+600 < now():
        label = "Checkout reservation expired"
    link = f'<p><a href="/api/download/{html.escape(token)}">Download MP4</a></p>' if state=="ready" else ""
    return HTMLResponse(f'<!doctype html><meta name="viewport" content="width=device-width"><title>Video order</title><main><h1>{label}</h1>{link}<p>You can close this tab. Refresh to check your order.</p></main>',
                        headers={"Cache-Control":"no-store","Referrer-Policy":"no-referrer"})


@app.get("/api/download/{token}")
def download(token: str):
    with db() as con:
        row = con.execute("SELECT id FROM orders WHERE token=? AND state='ready'", (token,)).fetchone()
    if not row or not (path := DATA / row["id"] / "film.mp4").is_file():
        raise HTTPException(404)
    with db() as con:
        con.execute("UPDATE orders SET download_at=? WHERE id=?", (now(),row["id"]))
    return FileResponse(path,media_type="video/mp4",filename="animation.mp4",headers={"Cache-Control":"private, no-store"})


def copy_signature(row, expires):
    return hmac.new(row["token"].encode(), f"backup/{row['id']}/{expires}".encode(), hashlib.sha256).hexdigest()


@app.get("/api/support-copy/{oid}")
def support_copy(oid: str, expires: int, sig: str):
    with db() as con:
        row = con.execute("SELECT id,token FROM orders WHERE id=? AND state='ready'",(oid,)).fetchone()
    if not row or not now() <= expires <= now()+1800 or not hmac.compare_digest(copy_signature(row,expires), sig):
        raise HTTPException(404)
    return FileResponse(DATA/oid/"film.mp4",media_type="video/mp4",headers={"Cache-Control":"private, no-store"})


def archive_pending():
    with db() as con:
        row = con.execute("SELECT id,token FROM orders WHERE state='ready' AND backup_sha IS NULL AND retry_backup<=? LIMIT 1",(now(),)).fetchone()
        if not row:
            return
        con.execute("UPDATE orders SET retry_backup=? WHERE id=?",(now()+1800,row["id"]))
    import modal
    with (DATA/row["id"]/"film.mp4").open("rb") as stream:
        sha = hashlib.file_digest(stream,"sha256").hexdigest()
    expires = now()+1800
    uploaded = modal.Function.from_name("vidbest-delivery-archive","backup").remote(row["id"],expires,copy_signature(row,expires),sha)
    if uploaded == sha:
        with db() as con:
            con.execute("UPDATE orders SET backup_sha=? WHERE id=?", (sha,row["id"]))


def render(oid):
    import modal
    with db() as con:
        row = con.execute("SELECT * FROM orders WHERE id=? AND state='rendering'", (oid,)).fetchone()
    if not row:
        raise RuntimeError("order not renderable")
    folder = DATA / oid
    folder.mkdir(mode=0o700,exist_ok=True)
    function = modal.Function.from_name(os.environ["MODAL_APP"],os.environ["MODAL_FUNCTION"])
    total = math.ceil(row["seconds"]/SHOT)
    segments = []
    for i in range(total):
        with db() as con:
            if con.execute("SELECT state FROM orders WHERE id=?",(oid,)).fetchone()[0] != "rendering":
                raise RuntimeError("order no longer active")
        seconds = min(SHOT,row["seconds"]-i*SHOT)
        prompt = f'{STYLES[row["style"]]}. {row["prompt"]}\nShot {i+1} of {total}.'
        data = function.remote(prompt,row["ratio"],seconds,int(oid[:8],16)+i)
        segment = folder / f"shot-{i:04}.mp4"
        segment.write_bytes(data)
        segments.append(f"file '{segment.name}'\n")
    (folder/"list.txt").write_text("".join(segments))
    subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","1","-i","list.txt",
                    "-t",str(row["seconds"]),"-c","copy","-movflags","+faststart","tmp.mp4"],cwd=folder,check=True)
    measured = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
                      "-of","csv=p=0",str(folder/"tmp.mp4")],text=True).strip())
    if abs(measured-row["seconds"]) > 0.15:
        raise RuntimeError("unexpected export duration")
    (folder/"tmp.mp4").replace(folder/"film.mp4")
    for p in folder.glob("shot-*.mp4"):
        p.unlink()


def mail(row):
    message = email.message.EmailMessage()
    message["From"],message["To"] = os.environ["SMTP_FROM"],row["email"]
    ready = row["state"] == "ready"
    message["Subject"] = "Your animation is ready" if ready else "Your animation order needs a refund review"
    message.set_content(("Download your watermark-free MP4" if ready else "Delivery could not finish. Your payment is under review.")+
                        "\nOrder reference: "+row["id"]+"\n"+BASE+"/api/status/"+row["token"])
    with smtplib.SMTP(os.environ["SMTP_HOST"],int(os.getenv("SMTP_PORT","587")),timeout=15) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        if os.getenv("SMTP_USER"):
            smtp.login(os.environ["SMTP_USER"],os.environ["SMTP_PASSWORD"])
        smtp.send_message(message)


def heartbeat():
    with db() as con:
        con.execute("INSERT OR REPLACE INTO runtime VALUES(1,?)", (now(),))


def worker():
    import signal
    lock = open(DATA / "worker.lock","a")
    fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
    with db() as con:
        # Uncertain submitted GPU calls require reconciliation to avoid duplicate spend.
        con.execute("UPDATE orders SET state='refund_review' WHERE state='rendering'")
    while True:
        heartbeat()
        with db() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM orders WHERE state='queued' ORDER BY paid LIMIT 1").fetchone()
            if row:
                con.execute("UPDATE orders SET state='rendering' WHERE id=?", (row["id"],))
        if row:
            deadline = row["paid"] + LIMIT
            ok = False
            if now() + row["eta"] <= deadline:
                proc = subprocess.Popen([sys.executable,__file__,"render",row["id"]], start_new_session=True)
                while proc.poll() is None:
                    heartbeat()
                    if now() >= deadline:
                        os.killpg(proc.pid,signal.SIGKILL)
                        break
                    time.sleep(1)
                ok = proc.wait() == 0 and now() <= deadline
            with db() as con:
                con.execute("UPDATE orders SET state=? WHERE id=? AND state='rendering'",
                            ("ready" if ok else "refund_review",row["id"]))
        with db() as con:
            notification = con.execute("""SELECT * FROM orders WHERE state IN ('ready','refund_review')
                AND mail_at=0 AND next_mail<=? ORDER BY paid LIMIT 1""", (now(),)).fetchone()
        if notification:
            try:
                mail(notification)
                sent = now()
            except (OSError,smtplib.SMTPException,KeyError):
                sent = 0
            with db() as con:
                con.execute("UPDATE orders SET mail_at=?,next_mail=? WHERE id=?", (sent,now()+300,notification["id"]))
        if not row:
            time.sleep(2)


if __name__ == "__main__":
    if sys.argv[1:] == ["archive"]:
        archive_pending()
    elif sys.argv[1:] == ["worker"]:
        worker()
    elif len(sys.argv)==3 and sys.argv[1]=="render":
        render(sys.argv[2])


