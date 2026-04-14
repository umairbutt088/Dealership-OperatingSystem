# DealershipOS (trial)

Local **dealership management** app for macOS: **FastAPI** + **SQLite** + **openpyxl**, with the **DealerOS v4** UI served to the browser. **Stock ID** (`STK-…`) is the **canonical primary key** for vehicles (not registration alone).

## Requirements

- Python 3.11+ (tested with Homebrew Python on macOS)
- The trial assets in `assets/`:
  - `DealerOS_v4_TRIAL_sanitised.html` (reference prototype)
  - `Master_Spreadsheet_TRIAL_sanitised.xlsx` (schema + import seed)

## One-time setup

```bash
cd /path/to/DealershipOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run (single command)

```bash
./run.sh
```

Open **http://127.0.0.1:8765/** in your browser.

### Manual run (with auto-reload)

```bash
source .venv/bin/activate
uvicorn dealershipos.main:app --reload --host 127.0.0.1 --port 8765
```

### Optional environment

| Variable | Meaning |
|----------|---------|
| `DEALERSHIP_DATA_DIR` | Override data directory (default: `./data`) |
| `DEALERSHIP_DATABASE_URL` | SQLite URL (default: `sqlite:///./data/dealershipos.db`) |

## Where data lives

| Path | Purpose |
|------|---------|
| `data/dealershipos.db` | SQLite database (vehicles, investors, expenses, collections, etc.) |
| `data/Cars/<STOCK_ID>/` | Per-vehicle folders: `Photos/`, `Documents/`, `ServiceHistory/`, `MOT/`, `Purchase/`, `Sale/`, `Delivery/`, `Collection/` |
| `data/Investors/<name>/` | Investor documents (created when used) |
| `data/Invoices/` | Reserved for invoice PDFs |
| `data/exports/` | Excel exports (`Master_Spreadsheet_export_*.xlsx`) |
| `data/uploads/` | Uploaded workbooks for import |

Deleting `data/dealershipos.db` and restarting will **re-import** the workbook from `assets/Master_Spreadsheet_TRIAL_sanitised.xlsx` if the vehicle table is empty.

## Excel workflow

- **Import:** use the **Import workbook** control in the top bar, or `POST /api/excel/import` with multipart file `file`. Query param `replace=true` wipes DB tables and reloads from the file (destructive).
- **Export:** **Export workbook** downloads a **new dated file** under `data/exports/`. The template is copied from `assets/Master_Spreadsheet_TRIAL_sanitised.xlsx`. Core sheets are updated **in place** by finding the header row and rewriting only the data rectangle (formula cells outside that rectangle are left as-is). **Stock Data** and **Sold Stock** include a **Stock ID** column for round-trip matching. Per-vehicle tabs (matched by registration embedded in the sheet name) are imported into `vehicle_line_items` and re-exported as **Item / Amount** blocks.

## API (selected)

- `GET /api/health` — liveness
- `GET /api/app-state` — JSON in the same shape as the prototype’s `APP_DATA` (includes `stock_id`, `deliveries`, etc.)
- `POST /api/vehicles` — create vehicle (creates `Cars/<STOCK_ID>/…` on disk)
- `PATCH /api/vehicles/{stock_id}` — update vehicle
- `GET /api/vehicles/{stock_id}/photos` — list photo files on disk
- `GET /api/vehicles/{stock_id}/photos/file/{filename}` — serve a photo file
- `POST /api/vehicles/{stock_id}/photos` — upload a file into `Photos/`
- `POST /api/collections` — add a collection row (SQLite)
- `POST /api/deliveries` — add a delivery row (SQLite)
- `POST /api/excel/import` — import workbook
- `GET /api/excel/export` — export workbook

## Assumptions

1. **Stock ID** (`STK-…`) is the canonical key. **Import** prefers a **Stock ID** column when present; otherwise rows match by **normalised plate**.
2. **Sold vs stock** is a single `vehicles` row with `is_sold`; Excel **Stock Data** and **Sold Stock** both feed this table.
3. **Front Sheet** and monthly summaries are imported when present; the UI still works with an empty summary (placeholder month).
4. **Per-vehicle workbook tabs** (not in the core sheet list) are matched to a vehicle when the **sheet name contains that car’s registration**; line items are stored in `vehicle_line_items` and synced on export.

## Remaining edge cases

- **Formulas inside** the same data columns we overwrite (e.g. a formula in the “Total Cost” cell) will still be replaced by a **static value** on export.
- **Photo tags / ordering** edited only in the UI are still mirrored in `localStorage` for AT/IG; server folder stores **files**; full tag persistence on disk is optional future work.
- **Authenticated** multi-user sessions if deployed off localhost.

## Phase 2 (optional)

- **Conflict resolution** when importing after local edits (merge strategies, not only replace-all).
- **Authenticated** sessions and audit log.

## Project layout

- `dealershipos/` — application package (`main.py`, `db/`, `api/`, `services/`)
- `static/` — split CSS/JS from the prototype + `index.html`
- `assets/` — original trial HTML/XLSX
- `scripts/patch_frontend.py` — optional: re-apply JS bootstrap pattern after replacing `static/js/app.js` from the prototype
