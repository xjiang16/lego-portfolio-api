<div align="center">
  <h1>LEGO Portfolio Tracker API</h1>
  <img src="lego_plants.jpg" width="700">
  <p> 🌸 A full-stack solution for tracking the financial growth of LEGO collections 🌸 </p>
</div>

<p>A comprehensive portfolio management system featuring a FastAPI backend and a Streamlit analytics dashboard.<p>

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit (Data Dashboard & Interactive Forms)
- **Visualization:** Plotly (Financial & Time-Series Charts)
- **Data Engineering:** Custom ETL Pipeline + Scheduled Price Snapshotting (idempotent, duplicate-safe)
- **Validation:** Pydantic (Request/Response Schemas)
- **Database:** SQLite with SQLAlchemy ORM
- **ORM:** SQLAlchemy (for Python-to-SQL translation)
- **Environment Management:** `python-dotenv` for secure config

## 🏛️ System Architecture
- **`lego_sets` table:** One row per owned set. Unique constraint on `set_number` prevents duplicate entries.
- **`price_history` table:** Append-only time-series log. Every snapshot run inserts a new row per set with a timestamp (`captured_at`), rather than overwriting the last known price — this is what powers the price trend chart on the dashboard.

### Market Simulation Engine
To decouple financial logic from external API latency, the system utilizes a **Mock Service** (`services/market.py`). This allows for consistent ROI calculations and local development while eBay/BrickLink API credentials are in the activation phase.

### Price History / Time-Series Tracking
`scripts/snapshot_prices.py` loops through every owned set, fetches its current market price, and appends a new row to `price_history`. Running this script periodically (manually today, on a schedule eventually) builds a genuine time-series dataset, which the dashboard visualizes as a per-set trend line via Plotly.

### Security & API Integration
- **Environment Management:** API keys are secured via `.env` and excluded from version control.
- **Authentication:** Prepared for `requests-oauthlib` handshakes for future marketplace integrations.

## Data Pipeline (ETL)
The project includes a dedicated, idempotent ETL script (`scripts/etl_pipeline.py`) to handle bulk data ingestion.
- **Extract:** Mimics fetching raw LEGO data from external sources.
- **Transform:** Cleans and standardizes messy data (e.g., stripping currency symbols, type conversion).
- **Load:** Checks for existing records by `set_number` before inserting, so the script can be safely re-run without creating duplicates or crashing on constraint violations.

## 🚀 Current Progress
- [x] Initialized FastAPI Backend & SQLite Schema
- [x] Developed idempotent ETL Pipeline for bulk data ingestion
- [x] Implemented **POST /add-set** with duplicate detection logic
- [x] Created **GET /portfolio/stats** with ROI and Net Profit logic
- [x] Developed Interactive Streamlit Dashboard
- [x] Integrated "Add New Set" Frontend Form with real-time inventory updates and error handling
- [x] Built `price_history` table + snapshot script for time-series price tracking
- [x] Added **GET /portfolio/history** endpoint and Price Trend visualization to dashboard
- [ ] Add automated test suite (pytest)
- [ ] Transition from Mock to Live eBay/Rebrickable Market Data
- [ ] Add User Authentication for private portfolios

## 💻 How to Run
1. **Setup Environment:**
    - Create venv: `python3 -m venv .venv` (use `python3`, not `python`, on Mac)
    - Activate: `source .venv/bin/activate` (Mac) or `.venv\Scripts\activate` (Windows)
    - Install dependencies: `.venv/bin/python -m pip install -r requirements.txt`

2. **Configure Secrets:**
    - Create a `.env` file in the root directory.
    - Add your API keys (e.g., `EBAY_APP_ID=your_id_here`).

3. **Initialize Data:**
    - Run ETL: `.venv/bin/python scripts/etl_pipeline.py`
    - Take a price snapshot: `.venv/bin/python scripts/snapshot_prices.py` (run this periodically to build price history over time)

4. **Start Server:**
    - Window 1: `.venv/bin/python -m uvicorn main:app --reload`
    - Window 2: `.venv/bin/python -m streamlit run dashboard.py`
    - Dashboard available at: `http://localhost:8501`. View Interactive Docs: `http://127.0.0.1:8000/docs`