from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

_engine_kw: dict = {"pool_pre_ping": True, "echo": settings.env == "development"}
if "sqlite" in settings.database_url:
    _engine_kw["connect_args"] = {"check_same_thread": False}
    _engine_kw["pool_pre_ping"] = False

engine = create_engine(settings.database_url, **_engine_kw)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
