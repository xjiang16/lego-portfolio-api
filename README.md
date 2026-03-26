<div align="center">
  <h1>LEGO Portfolio Tracker API</h1>
  <img src="lego_plants.jpg" width="700">
  <p> 🌸Tracking the growth of favorite Lego collections🌸</p>
</div>

A FastAPI-based backend to track LEGO set collections, purchase prices, and market values.

## Tech Stack
- **Framework:** FastAPI
- **Data Engineering:** Custom ETL Pipeline (Extract, Transform, Load)
- **Validation:** Pydantic
- **Database:** SQLite
- **ORM:** SQLAlchemy (for Python-to-SQL translation)
- **Security:** `python-dotenv` for environment variable management

## Database Architecture
The project uses **SQLite** for local data persistence and **SQLAlchemy** as the ORM.
- **Table Name:** `lego_sets`
- **Primary Key:** `id` (Auto-incrementing Integer)
- **Unique Constraint:** `set_number` (Prevents duplicate entries)

### Security & API Integration
To protect sensitive credentials (eBay/Rebrickable/BrickLink), the project utilizes a `.env` architecture.
- **Environment Management:** Keys are stored locally and excluded from version control via `.gitignore`.
- **Authentication:** Integrated `requests-oauthlib` for future OAuth 1.1 handshakes with marketplace APIs.

## Data Pipeline (ETL)
The project includes a dedicated ETL script (`scripts/etl_pipeline.py`) to handle bulk data ingestion.
- **Extract:** Mimics fetching raw LEGO data from external sources.
- **Transform:** Cleans and standardizes messy data (e.g., stripping currency symbols, type conversion).
- **Load:** Performs bulk inserts into the SQLite database with error handling and rollbacks.
- 
## Current Progress
- [x] Initialized Virtual Environment and FastAPI
- [x] Created Data Schemas using Pydantic
- [x] Configured SQLAlchemy and SQL Models
- [x] Developed ETL Pipeline for bulk data ingestion 
- [x] Implemented **POST /add-set** with duplicate detection logic
- [x] Created **GET /portfolio/stats** for real-time investment tracking
- [ ] Integrate Live eBay/BrickLink Market Data (Pending API Approval)
- [ ] Implement ROI and Net Profit visualization

## How to Run
1. **Setup Environment:**
    - Create venv: `python -m venv .venv`
    - Activate: `source .venv/bin/activate`
    - Install dependencies: `pip install -r requirements.txt`

2. **Configure Secrets:**
    - Create a `.env` file in the root directory.
    - Add your API keys (e.g., `EBAY_APP_ID=your_id_here`).

3. **Initialize Data:**
    - Run ETL: `python scripts/etl_pipeline.py`

4. **Start Server:**
    - `uvicorn main:app --reload`
    - View Interactive Docs: `http://127.0.0.1:8000/docs`