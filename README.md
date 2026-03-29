<div align="center">
  <h1>LEGO Portfolio Tracker API</h1>
  <img src="lego_plants.jpg" width="700">
  <p> 🌸 A full-stack solution for tracking the financial growth of LEGO collections 🌸 </p>
</div>

<p>A comprehensive portfolio management system featuring a FastAPI backend and a Streamlit analytics dashboard.<p>

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** Streamlit (Data Dashboard & Interactive Forms)
- **Visualization:** Plotly (Financial Charts)
- **Data Engineering:** Custom ETL Pipeline (Pandas-based extraction & cleaning)
- **Validation:** Pydantic (Request/Response Schemas)
- **Database:** SQLite with SQLAlchemy ORM
- **ORM:** SQLAlchemy (for Python-to-SQL translation)
- **Security:** `python-dotenv` for environment variable management

## 🏛️ System Architecture
### Database Layer
- **Table:** `lego_sets`
- **Integrity:** Implemented unique constraints on `set_number` to ensure data consistency and prevent duplicate entries.

### Market Simulation Engine
To decouple financial logic from external API latency, the system utilizes a **Mock Service** (`services/market.py`). This allows for consistent ROI calculations and local development while eBay/BrickLink API credentials are in the activation phase.

### Security & API Integration
- **Environment Management:** API keys are secured via `.env` and excluded from version control.
- **Authentication:** Prepared for `requests-oauthlib` handshakes for future marketplace integrations.

## Data Pipeline (ETL)
The project includes a dedicated ETL script (`scripts/etl_pipeline.py`) to handle bulk data ingestion.
- **Extract:** Mimics fetching raw LEGO data from external sources.
- **Transform:** Cleans and standardizes messy data (e.g., stripping currency symbols, type conversion).
- **Load:** Performs bulk inserts into the SQLite database with error handling and rollbacks.

## 🚀Current Progress
- [x] Initialized FastAPI Backend & SQLite Schema
- [x] Developed ETL Pipeline for bulk data ingestion
- [x] Implemented **POST /add-set** with duplicate detection logic
- [x] Created **GET /portfolio/stats** with ROI and Net Profit logic
- [x] **Developed Interactive Streamlit Dashboard**
- [x] **Integrated "Add New Set" Frontend Form** for real-time inventory updates
- [ ] Transition from Mock to Live eBay Market Data
- [ ] Add User Authentication for private portfolios

## 💻 How to Run
1. **Setup Environment:**
    - Create venv: `python -m venv .venv`
    - Activate: `source .venv/bin/activate` (Mac) or `.venv\Scripts\activate` (Windows)
    - Install dependencies: `pip install -r requirements.txt`

2. **Configure Secrets:**
    - Create a `.env` file in the root directory.
    - Add your API keys (e.g., `EBAY_APP_ID=your_id_here`).

3. **Initialize Data:**
    - Run ETL: `python scripts/etl_pipeline.py`

4. **Start Server:**
    - Window 1: `uvicorn main:app --reload`
    - Window 2: `streamlit run dashboard.py`
    - Dashboard available at: `http://localhost:8501`. View Interactive Docs: `http://127.0.0.1:8000/docs`