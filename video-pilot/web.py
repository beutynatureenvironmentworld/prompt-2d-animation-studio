from pathlib import Path
from fastapi.responses import FileResponse
from backend import app

@app.get("/", include_in_schema=False)
def studio():
    return FileResponse(Path(__file__).with_name("index.html"), headers={
        "Cache-Control": "no-cache",
        "Referrer-Policy": "no-referrer",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action https://sandbox.payhere.lk https://www.payhere.lk",
    })
