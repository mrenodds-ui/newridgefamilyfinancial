"""Retired legacy host for New Ridge Family Financial.

The mockup pages moved to NewRidgeFinancial 2.0 (port 8096).
Use StartNewRidgeFinancial2.bat or scripts/start_program_2.ps1.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="New Ridge Family Financial (retired)")

_RETIRED = {
    "status": "retired",
    "message": "This legacy program no longer serves the UI.",
    "use_instead": {
        "program": "NewRidgeFinancial 2.0",
        "start": "StartNewRidgeFinancial2.bat",
        "url": "http://127.0.0.1:8096/app",
    },
}


@app.get("/")
@app.get("/health")
@app.get("/app")
@app.get("/app/{request_path:path}")
def retired():
    return JSONResponse(status_code=410, content=_RETIRED)
