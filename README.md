<div align="center">
  <h1>LEGO Portfolio Tracker API</h1>
  <img src="lego_plants.jpg" width="700">
  <p> 🌸Tracking the growth of favorite Lego collections🌸</p>
</div>

A FastAPI-based backend to track LEGO set collections, purchase prices, and market values.

## Tech Stack
- **Framework:** FastAPI
- **Validation:** Pydantic
- **Database:** SQLite
- **ORM:** SQLAlchemy (for Python-to-SQL translation)

## Database Architecture
The project uses **SQLite** for local data persistence and **SQLAlchemy** as the ORM.
- **Table Name:** `lego_sets`
- **Primary Key:** `id` (Auto-incrementing Integer)
- **Unique Constraint:** `set_number` (Prevents duplicate entries)

## Current Progress
- [x] Initialized Virtual Environment and FastAPI
- [x] Created Data Schemas using Pydantic
- [x] Implemented POST endpoint for adding sets
- [x] Configured SQLAlchemy Engine and Base connection
- [x] Defined SQL Models and Initialized SQLite Database

## How to Run
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Windows)
3. Install tools: `pip install -r requirements.txt`
4. Start the server: `uvicorn main:app --reload`
5. View docs: `http://127.0.0.1:8000/docs`