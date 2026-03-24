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

## Database Architecture
The project uses **SQLite** for local data persistence and **SQLAlchemy** as the ORM.
- **Table Name:** `lego_sets`
- **Primary Key:** `id` (Auto-incrementing Integer)
- **Unique Constraint:** `set_number` (Prevents duplicate entries)

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
- [x] Implemented GET /sets endpoint for collection viewing 
- [ ] Implement Portfolio Valuation logic (Total Value, ROI)

## How to Run
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Windows)
3. Install tools: `pip install -r requirements.txt`
4. Run the ETL Pipeline: `python scripts/etl_pipeline.py` (Loads initial data)
4. Start the server: `uvicorn main:app --reload`
5. View docs: `http://127.0.0.1:8000/docs`