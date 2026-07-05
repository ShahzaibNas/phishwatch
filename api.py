"""Web API for PhishWatch — the one-shot scan service."""

from fastapi import FastAPI
from fastapi import Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from src.scanner import scan_domain
import re
import time
from collections import defaultdict

from fastapi import HTTPException

app = FastAPI(title="PhishWatch")
# --- crude in-memory rate limiter (per IP) ---
# Fine for a single-server MVP. A real deployment would use Redis
# so limits survive restarts and work across multiple servers.
_RATE_LIMIT = 5          # scans allowed...
_RATE_WINDOW = 60        # ...per this many seconds
_hits: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(ip: str):
    now = time.time()
    # keep only timestamps within the window
    _hits[ip] = [t for t in _hits[ip] if now - t < _RATE_WINDOW]
    if len(_hits[ip]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many scans. Please wait a minute and try again.",
        )
    _hits[ip].append(now)


# --- domain input validation ---
_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,}$"
)


def _validate_domain(domain: str) -> str:
    domain = domain.strip().lower()
    if not _DOMAIN_RE.match(domain):
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid domain like example.com",
        )
    return domain

class ScanRequest(BaseModel):
    domain: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "PhishWatch"}


@app.post("/api/scan")
def scan(request: ScanRequest, http_request: Request):
    client_ip = http_request.client.host
    _check_rate_limit(client_ip)
    domain = _validate_domain(request.domain)

    results = scan_domain(domain)
    return {
        "target": domain,
        "count": len(results),
        "results": results,
    }
app.mount("/", StaticFiles(directory="static", html=True), name="static")