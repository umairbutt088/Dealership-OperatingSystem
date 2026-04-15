from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from time import monotonic
from typing import Any, Optional
from urllib.parse import unquote, quote

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from dealershipos.config import settings
from dealershipos.db.models import CollectionRow, DeliveryRow, Vehicle, new_stock_id
from dealershipos.db.session import get_db
from dealershipos.services.app_state import build_app_state, vehicle_to_sold_dict, vehicle_to_stock_dict
from dealershipos.services.excel_sync import export_workbook, import_workbook
from dealershipos.services.folders import ensure_car_folders, photo_dir
from dealershipos.services.plates import norm_plate

router = APIRouter(prefix="/api", tags=["api"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_TEMPLATE = PROJECT_ROOT / "assets" / "Master_Spreadsheet_TRIAL_sanitised.xlsx"
_APP_STATE_CACHE: dict[str, Any] = {"payload": None, "expires_at": 0.0}


def _invalidate_app_state_cache() -> None:
    _APP_STATE_CACHE["payload"] = None
    _APP_STATE_CACHE["expires_at"] = 0.0


class VehicleCreate(BaseModel):
    plate: str
    model: str = ""
    source: str = ""
    investor: str = ""
    purchase_price: float = 0
    recon_cost: float = 0
    notes: str = ""
    status: str = "In Stock"


class VehiclePatch(BaseModel):
    model: Optional[str] = None
    source: Optional[str] = None
    investor: Optional[str] = None
    purchase_price: Optional[float] = None
    recon_cost: Optional[float] = None
    total_cost: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    days_in_stock: Optional[int] = None
    month: Optional[str] = None
    is_sold: Optional[bool] = None
    sold_price: Optional[float] = None
    profit: Optional[float] = None
    date_sold: Optional[str] = None
    investor_profit: Optional[float] = None
    sa_profit: Optional[float] = None
    invoice_number: Optional[str] = None


class CollectionCreate(BaseModel):
    source: str = ""
    plate: str
    model: str = ""
    date_won: Optional[str] = None
    location: str = ""
    post_code: str = ""
    how_far: str = ""
    collection_date: str = ""
    number: str = ""
    notes: str = ""


class DeliveryCreate(BaseModel):
    plate: str
    model: str = ""
    addr: str = ""
    date: Optional[str] = None
    scheduled_date: Optional[str] = None
    driver: str = ""
    cost: float = 0
    status: str = "Pending"
    notes: str = ""


def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/app-state")
def app_state(db: Session = Depends(get_db)) -> dict[str, Any]:
    now = monotonic()
    cached = _APP_STATE_CACHE.get("payload")
    if cached is not None and now < float(_APP_STATE_CACHE.get("expires_at", 0.0)):
        return cached
    payload = build_app_state(db)
    _APP_STATE_CACHE["payload"] = payload
    _APP_STATE_CACHE["expires_at"] = now + max(1, int(settings.app_state_cache_ttl_seconds))
    return payload


@router.post("/vehicles")
def create_vehicle(body: VehicleCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    np = norm_plate(body.plate)
    if not np:
        raise HTTPException(400, "plate required")
    existing = db.execute(select(Vehicle).where(Vehicle.plate_norm == np)).scalar_one_or_none()
    if existing:
        raise HTTPException(409, "vehicle with this plate already exists")
    tid = new_stock_id()
    price = body.purchase_price or 0
    recon = body.recon_cost or 0
    month = date.today().replace(day=1).isoformat()
    v = Vehicle(
        stock_id=tid,
        plate=body.plate.strip().upper(),
        plate_norm=np,
        model=body.model or None,
        month=month,
        date_acquired=date.today(),
        source=body.source or None,
        investor=body.investor or None,
        purchase_price=price,
        recon_cost=recon,
        total_cost=price + recon,
        status=body.status,
        notes=body.notes or None,
        days_in_stock=0,
        is_sold=False,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    ensure_car_folders(v.stock_id)
    _invalidate_app_state_cache()
    return vehicle_to_stock_dict(v)


@router.post("/collections")
def create_collection(body: CollectionCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    np = norm_plate(body.plate)
    cr = CollectionRow(
        source=body.source or None,
        date_won=_parse_date(body.date_won),
        plate=body.plate.strip().upper(),
        plate_norm=np or None,
        model=body.model or None,
        location=body.location or None,
        post_code=body.post_code or None,
        how_far=body.how_far or None,
        collection_date=body.collection_date or None,
        number=body.number or None,
        additional_notes=body.notes or None,
    )
    if np:
        v = db.execute(select(Vehicle).where(Vehicle.plate_norm == np)).scalar_one_or_none()
        if v:
            cr.stock_id = v.stock_id
    db.add(cr)
    db.commit()
    db.refresh(cr)
    _invalidate_app_state_cache()
    return {"ok": True, "id": cr.id}


@router.post("/deliveries")
def create_delivery(body: DeliveryCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    np = norm_plate(body.plate)
    dr = DeliveryRow(
        plate=body.plate.strip().upper(),
        plate_norm=np or None,
        model=body.model or None,
        addr=body.addr or None,
        date=_parse_date(body.date),
        scheduled_date=_parse_date(body.scheduled_date or body.date),
        driver=body.driver or None,
        cost=body.cost,
        status=body.status or "Pending",
        notes=body.notes or None,
    )
    if np:
        v = db.execute(select(Vehicle).where(Vehicle.plate_norm == np)).scalar_one_or_none()
        if v:
            dr.stock_id = v.stock_id
    db.add(dr)
    db.commit()
    db.refresh(dr)
    _invalidate_app_state_cache()
    return {"ok": True, "id": dr.id}


@router.patch("/vehicles/{stock_id}")
def patch_vehicle(stock_id: str, body: VehiclePatch, db: Session = Depends(get_db)) -> dict[str, Any]:
    v = db.get(Vehicle, stock_id)
    if not v:
        raise HTTPException(404, "vehicle not found")
    data = body.model_dump(exclude_unset=True)
    if "date_sold" in data:
        ds = data.pop("date_sold")
        v.date_sold = _parse_date(ds) if ds else None
    for k, val in data.items():
        setattr(v, k, val)
    if v.purchase_price is not None and v.recon_cost is not None:
        v.total_cost = (v.purchase_price or 0) + (v.recon_cost or 0)
    db.commit()
    db.refresh(v)
    ensure_car_folders(v.stock_id)
    _invalidate_app_state_cache()
    return vehicle_to_sold_dict(v) if v.is_sold else vehicle_to_stock_dict(v)


@router.post("/excel/import")
async def excel_import(
    file: UploadFile = File(...),
    replace: bool = False,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    dest = settings.data_dir / "uploads"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / file.filename.replace("/", "_")
    raw = await file.read()
    path.write_bytes(raw)
    counts = import_workbook(path, db, replace=replace)
    _invalidate_app_state_cache()
    return {"imported": counts, "path": str(path)}


@router.get("/excel/export")
def excel_export(db: Session = Depends(get_db)) -> FileResponse:
    if not DEFAULT_TEMPLATE.is_file():
        raise HTTPException(500, "template workbook missing from assets/")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = settings.data_dir / "exports" / f"Master_Spreadsheet_export_{stamp}.xlsx"
    export_workbook(DEFAULT_TEMPLATE, db, out)
    return FileResponse(
        out,
        filename=out.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/vehicles/{stock_id}/photos")
def list_vehicle_photos(stock_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    v = db.get(Vehicle, stock_id)
    if not v:
        raise HTTPException(404, "vehicle not found")
    pdir = photo_dir(stock_id)
    if not pdir.is_dir():
        return {"photos": []}
    photos: list[dict[str, Any]] = []
    for p in sorted(pdir.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".bmp"):
            continue
        qn = quote(p.name, safe="")
        photos.append(
            {
                "id": p.name,
                "url": f"/api/vehicles/{stock_id}/photos/file/{qn}",
                "tag": "misc",
                "cover": len(photos) == 0,
            }
        )
    return {"photos": photos}


@router.get("/vehicles/{stock_id}/photos/file/{filename}")
def serve_vehicle_photo(stock_id: str, filename: str, db: Session = Depends(get_db)) -> FileResponse:
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(400, "invalid filename")
    v = db.get(Vehicle, stock_id)
    if not v:
        raise HTTPException(404, "vehicle not found")
    fn = unquote(filename)
    base = photo_dir(stock_id).resolve()
    full = (base / fn).resolve()
    if not str(full).startswith(str(base)):
        raise HTTPException(400, "invalid path")
    if not full.is_file():
        raise HTTPException(404, "file not found")
    return FileResponse(full)


@router.post("/vehicles/{stock_id}/photos")
async def upload_photo(stock_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, str]:
    v = db.get(Vehicle, stock_id)
    if not v:
        raise HTTPException(404, "vehicle not found")
    ensure_car_folders(stock_id)
    pdir = photo_dir(stock_id)
    safe = file.filename.replace("/", "_") if file.filename else "photo.bin"
    path = pdir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe}"
    path.write_bytes(await file.read())
    qn = quote(path.name, safe="")
    return {
        "path": str(path.relative_to(settings.data_dir)),
        "url": f"/api/vehicles/{stock_id}/photos/file/{qn}",
        "filename": path.name,
    }
