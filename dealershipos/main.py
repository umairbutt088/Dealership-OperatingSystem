from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from dealershipos.api.routes import router as api_router
from dealershipos.config import settings
from dealershipos.db.session import SessionLocal, init_db
from dealershipos.services.excel_sync import import_workbook
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
ASSETS_XLSX = PROJECT_ROOT / "assets" / "Master_Spreadsheet_TRIAL_sanitised.xlsx"

app = FastAPI(title="DealershipOS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    if ASSETS_XLSX.is_file():
        db = SessionLocal()
        try:
            from sqlalchemy import func, select

            from dealershipos.db.models import Vehicle

            cnt = db.scalar(select(func.count()).select_from(Vehicle))
            if cnt == 0:
                import_workbook(ASSETS_XLSX, db, replace=False)
        except Exception as e:
            import logging

            logging.exception("Initial Excel import failed: %s", e)
        finally:
            db.close()


app.include_router(api_router)

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.is_file():
        return FileResponse(PROJECT_ROOT / "assets" / "DealerOS_v4_TRIAL_sanitised.html")
    return FileResponse(index_path)
