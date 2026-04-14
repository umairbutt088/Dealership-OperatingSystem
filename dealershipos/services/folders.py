from pathlib import Path

from dealershipos.config import settings

CAR_SUBFOLDERS = (
    "Photos",
    "Documents",
    "ServiceHistory",
    "MOT",
    "Purchase",
    "Sale",
    "Delivery",
    "Collection",
)


def ensure_car_folders(stock_id: str) -> Path:
    """Create `Cars/<STOCK_ID>/...` on disk; returns the vehicle root path."""
    root = settings.cars_base / stock_id
    for name in CAR_SUBFOLDERS:
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def ensure_investor_folder(slug: str) -> Path:
    """Sanitized investor name for a folder under Investors/."""
    safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in slug).strip() or "unknown"
    root = settings.investors_base / safe
    for sub in ("Documents", "Agreements", "Invoices"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def photo_dir(stock_id: str) -> Path:
    return settings.cars_base / stock_id / "Photos"
