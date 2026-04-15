# DealershipOS

DealershipOS is a local dealership management system for macOS. It runs a FastAPI backend with a SQLite database and serves the existing DealerOS UI, while keeping Stock ID (`STK-...`) as the canonical key across stock, sold, deliveries, collections, photos, and Excel sync.

## What The System Does

- Manage vehicle stock and sold lifecycle using `stock_id` as the primary reference.
- Track investors, expenses, deliveries, collections, and summaries in SQLite.
- Import from and export to the dealership Excel workbook structure.
- Create real folder structures on disk for each vehicle and store media/documents.
- Serve the existing frontend layout and flows locally for daily internal use.

## Mac Setup

### Prerequisites

- macOS (local machine/server)
- Python 3.11+

### Dependency Install Steps

```bash
cd /path/to/DealershipOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Exact run command:

```bash
./run.sh
```

Default local URL:

- [http://127.0.0.1:8765/](http://127.0.0.1:8765/)

You can override bind settings via environment variables:

```bash
HOST=0.0.0.0 PORT=8765 ./run.sh
```

## Data And Files

- Database: `data/dealershipos.db`
- Vehicle folders: `data/Cars/<STOCK_ID>/`
  - `Photos/`, `Documents/`, `ServiceHistory/`, `MOT/`, `Purchase/`, `Sale/`, `Delivery/`, `Collection/`
- Investor folders: `data/Investors/<name>/`
- Exported workbooks: `data/exports/`
- Uploaded workbooks: `data/uploads/`

## Render Deployment (Free Tier)

This project includes a `render.yaml` blueprint for one-click setup.

### Quick Deploy

1. Push this repo to GitHub.
2. In Render, create a new **Web Service** from the repo.
3. Render auto-detects `render.yaml` and uses:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn dealershipos.main:app --host 0.0.0.0 --port $PORT`
4. Ensure environment variables are set:
   - `DEALERSHIP_DATA_DIR=/var/data`
   - `DEALERSHIP_DATABASE_URL=sqlite:////var/data/dealershipos.db`
5. Add a persistent disk mounted at `/var/data` if available in your Render plan.

### Important Free-Tier Note

If persistent disk is not available on your free plan, SQLite data/uploads/photos may reset during restarts or redeploys.

## Known Limitations (Honest + Concise)

- Some advanced UI modules still use local browser state for non-critical metadata (e.g. parts of listing/tag helpers).
- Excel export can overwrite formula cells if formulas are placed inside rewritten data columns.
- Conflict-resolution strategy for “Excel changed + app changed” is basic; replace-import is available, but merge logic is not fully advanced.
- No authentication/multi-user permission model yet (single local team environment).
