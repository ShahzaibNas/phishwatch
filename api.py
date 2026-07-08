"""Web API for PhishWatch — the one-shot scan service and the
monitoring dashboard's read/write endpoints."""

import re
import time
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.scanner import scan_domain
from src.db import init_db, get_alerts, get_brands, add_brand

app = FastAPI(title="PhishWatch")


@app.on_event("startup")
def _startup():
    init_db()      # ensure tables exist when the API boots


# ---------- rate limiter (per IP, in-memory) ----------
# Fine for a single-server MVP. Production would use Redis so limits
# survive restarts and work across multiple servers.
_RATE_LIMIT = 5
_RATE_WINDOW = 60
_hits: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(ip: str):
    now = time.time()
    _hits[ip] = [t for t in _hits[ip] if now - t < _RATE_WINDOW]
    if len(_hits[ip]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a minute and try again.",
        )
    _hits[ip].append(now)


# ---------- domain validation ----------
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


# ---------- request models ----------
class ScanRequest(BaseModel):
    domain: str


class BrandRequest(BaseModel):
    name: str
    domain: str


# ---------- health ----------
@app.get("/health")
def health():
    return {"status": "ok", "service": "PhishWatch"}


# ---------- one-shot scan ----------
@app.post("/api/scan")
def scan(request: ScanRequest, http_request: Request):
    _check_rate_limit(http_request.client.host)
    domain = _validate_domain(request.domain)
    results = scan_domain(domain)
    return {"target": domain, "count": len(results), "results": results}


# ---------- monitoring: alerts ----------
@app.get("/api/alerts")
def api_alerts(min_score: int = 0):
    return {"alerts": get_alerts(min_score=min_score)}


# ---------- monitoring: brands ----------
@app.get("/api/brands")
def api_brands():
    return {"brands": get_brands()}


@app.post("/api/brands")
def api_add_brand(req: BrandRequest, http_request: Request):
    _check_rate_limit(http_request.client.host)
    domain = _validate_domain(req.domain)
    name = req.name.strip()[:64] or domain.split(".")[0]
    return add_brand(name, domain)


# ---------- Delete brands ----------
@app.delete("/api/brands/{brand_id}")
def api_delete_brand(brand_id: int):
    from src.db import delete_brand
    if not delete_brand(brand_id):
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"deleted": True, "id": brand_id}

# ---------- static files (MUST be last — catch-all mount) ----------
app.mount("/", StaticFiles(directory="static", html=True), name="static")