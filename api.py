"""Web API for PhishWatch — the one-shot scan service."""

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from src.scanner import scan_domain

app = FastAPI(title="PhishWatch")


class ScanRequest(BaseModel):
    domain: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "PhishWatch"}


@app.post("/api/scan")
def scan(request: ScanRequest):
    """Scan a domain for live lookalike domains.

    Returns the target and a list of scored results, highest first.
    """
    results = scan_domain(request.domain)
    return {
        "target": request.domain,
        "count": len(results),
        "results": results,
    }
app.mount("/", StaticFiles(directory="static", html=True), name="static")