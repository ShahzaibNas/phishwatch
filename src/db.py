"""Database models and access layer for PhishWatch.

Uses SQLModel (SQLAlchemy + Pydantic) so table rows are Python
objects. Develops against SQLite locally; the same models run on
PostgreSQL in production by changing only DATABASE_URL.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session, select, desc


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------- models ----------

class Brand(SQLModel, table=True):
    """A brand being continuously monitored."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    domain: str = Field(index=True)
    created_at: datetime = Field(default_factory=_utcnow)


class Alert(SQLModel, table=True):
    """A detection produced by the continuous watcher."""
    id: Optional[int] = Field(default=None, primary_key=True)
    domain: str = Field(index=True)          # the suspicious domain
    brand: str = Field(index=True)           # which brand it targets
    match_type: str                          # permutation | keyword
    score: int
    detail: str
    seen_at: datetime = Field(default_factory=_utcnow, index=True)


# ---------- engine & session ----------

# One line to switch databases later: swap this URL for a
# PostgreSQL one (postgresql://user:pass@host/dbname) in production.
DATABASE_URL = "sqlite:///phishwatch.db"

# check_same_thread=False: the web server and the watcher access
# the DB from different threads/processes.
engine = create_engine(
    DATABASE_URL,
    echo=False,                                  # set True to see SQL
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables. Safe to call repeatedly."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Open a new database session (a unit of work)."""
    return Session(engine)


# ---------- write helpers (used by the watcher) ----------

def save_alert(brand: str, domain: str, match_type: str,
               score: int, detail: str) -> None:
    """Persist one detection as an Alert row."""
    with get_session() as s:
        s.add(Alert(
            domain=domain, brand=brand,
            match_type=match_type, score=score, detail=detail,
        ))
        s.commit()


def load_brands() -> list[dict]:
    """Brands in the shape BrandMatcher expects:
    [{"name": ..., "domain": ...}, ...]."""
    with get_session() as s:
        rows = s.exec(select(Brand)).all()
        return [{"name": b.name, "domain": b.domain} for b in rows]


# ---------- read/write helpers (used by the web API) ----------

def get_alerts(limit: int = 200, min_score: int = 0) -> list[dict]:
    """Recent alerts, newest first, optionally filtered by score."""
    with get_session() as s:
        q = select(Alert)
        if min_score > 0:
            q = q.where(Alert.score >= min_score)
        q = q.order_by(desc(Alert.seen_at)).limit(limit)
        rows = s.exec(q).all()
        return [{
            "domain": a.domain, "brand": a.brand,
            "match_type": a.match_type, "score": a.score,
            "detail": a.detail, "seen_at": a.seen_at.isoformat(),
        } for a in rows]


def get_brands() -> list[dict]:
    """All monitored brands (full detail for the dashboard)."""
    with get_session() as s:
        return [{"id": b.id, "name": b.name, "domain": b.domain,
                 "created_at": b.created_at.isoformat()}
                for b in s.exec(select(Brand)).all()]


def add_brand(name: str, domain: str) -> dict:
    """Add a brand to monitor. Ignores exact duplicate domains."""
    with get_session() as s:
        existing = s.exec(
            select(Brand).where(Brand.domain == domain)
        ).first()
        if existing:
            return {"id": existing.id, "name": existing.name,
                    "domain": existing.domain, "duplicate": True}
        b = Brand(name=name, domain=domain)
        s.add(b); s.commit(); s.refresh(b)
        return {"id": b.id, "name": b.name, "domain": b.domain,
                "duplicate": False}

def delete_brand(brand_id: int) -> bool:
    """Remove a monitored brand by id. Returns True if deleted."""
    with get_session() as s:
        b = s.get(Brand, brand_id)
        if not b:
            return False
        s.delete(b)
        s.commit()
        return True                