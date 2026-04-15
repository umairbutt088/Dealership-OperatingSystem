from collections.abc import Generator
from pathlib import Path
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from dealershipos.config import settings
from dealershipos.db.models import Base

logger = logging.getLogger(__name__)


def _ensure_storage_paths() -> None:
    try:
        Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
        settings.cars_base.mkdir(parents=True, exist_ok=True)
        settings.investors_base.mkdir(parents=True, exist_ok=True)
        settings.invoices_base.mkdir(parents=True, exist_ok=True)
        return
    except PermissionError:
        fallback = Path("/tmp/dealershipos-data")
        fallback.mkdir(parents=True, exist_ok=True)
        old_data_dir = Path(settings.data_dir)
        settings.data_dir = fallback
        # If DB URL still points at old local-path sqlite, move it to fallback too.
        if settings.database_url.startswith("sqlite:///"):
            db_name = Path(settings.sqlite_path).name
            settings.database_url = f"sqlite:////{fallback / db_name}"
        settings.cars_base.mkdir(parents=True, exist_ok=True)
        settings.investors_base.mkdir(parents=True, exist_ok=True)
        settings.invoices_base.mkdir(parents=True, exist_ok=True)
        logger.warning("Falling back data_dir from %s to %s", old_data_dir, fallback)


_ensure_storage_paths()

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
