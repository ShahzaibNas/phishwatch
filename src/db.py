"""Database models and connection for PhishWatch.

Uses SQLModel (SQLAlchemy + Pydantic) so table rows are Python
objects. Develops against SQLite locally; the same models run on
PostgreSQL in production by changing only DATABASE_URL.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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


# --- engine & session setup ---
# One line to switch databases later: swap this URL for a
# PostgreSQL one (postgresql://user:pass@host/dbname) in production.
DATABASE_URL = "sqlite:///phishwatch.db"

# check_same_thread=False: needed because the web server and the
# watcher access the DB from different threads/processes.
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