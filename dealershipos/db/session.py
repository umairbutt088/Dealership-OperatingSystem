from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dealershipos.config import settings
from dealershipos.db.models import Base

_data_dir = Path(settings.data_dir)
_data_dir.mkdir(parents=True, exist_ok=True)
settings.cars_base.mkdir(parents=True, exist_ok=True)
settings.investors_base.mkdir(parents=True, exist_ok=True)
settings.invoices_base.mkdir(parents=True, exist_ok=True)

_sqlite_url = f"sqlite:///{settings.sqlite_path}"

engine = create_engine(
    _sqlite_url,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
