from sqlmodel import SQLModel, create_engine, Session, select

from src.db import Brand, Alert


def _memory_session():
    # In-memory SQLite: a fresh throwaway DB per test, no file,
    # no network — fast and isolated, like your mocked tests.
    engine = create_engine("sqlite://",
                           connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_can_persist_and_read_brand():
    s = _memory_session()
    s.add(Brand(name="paypal", domain="paypal.com"))
    s.commit()
    brands = s.exec(select(Brand)).all()
    assert len(brands) == 1
    assert brands[0].domain == "paypal.com"
    assert brands[0].id == 1          # primary key auto-assigned


def test_can_persist_alert_with_score():
    s = _memory_session()
    s.add(Alert(domain="paypa1.com", brand="paypal",
                match_type="permutation", score=7, detail="test"))
    s.commit()
    a = s.exec(select(Alert)).one()
    assert a.score == 7
    assert a.seen_at is not None       # default timestamp applied