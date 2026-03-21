# LEGO Portfolio Tracker API

A FastAPI-based backend to track LEGO set collections, purchase prices, and market values.

## Current Progress
- [x] Initialized Virtual Environment and FastAPI
- [x] Created Data Schemas using Pydantic
- [x] Implemented POST endpoint for adding sets

## How to Run
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Windows)
3. Install tools: `pip install -r requirements.txt`
4. Start the server: `uvicorn main:app --reload`
5. View docs: `http://127.0.0.1:8000/docs`