from fastapi import FastAPI
from fastapi import HTTPException
import model
from database import engine, SessionLocal
import schemas
from services import market
import os
import requests
from dotenv import load_dotenv

load_dotenv()
REBRICKABLE_API_KEY = os.getenv("REBRICKABLE_API_KEY")
REBRICKABLE_HEADERS = {"Authorization": f"key {REBRICKABLE_API_KEY}"}

model.Base.metadata.create_all(bind=engine)

def seed_if_empty():
    """If the DB is empty (e.g. fresh deploy on ephemeral storage), populate demo data."""
    db = SessionLocal()
    try:
        if db.query(model.LegoSet).count() == 0:
            print("Database empty — seeding demo data...")
            demo_sets = [
                {"set_name": "Tiny Plants", "set_number": "10329", "theme": "Botanicals", "purchase_price": 49.99, "quantity": 1, "condition": "New", "year": 2023, "num_parts": 758, "image_url": "https://cdn.rebrickable.com/media/sets/10329-1/128976.jpg"},
                {"set_name": "Succulents", "set_number": "10309", "theme": "Botanicals", "purchase_price": 44.99, "quantity": 1, "condition": "New", "year": 2022, "num_parts": 771, "image_url": "https://cdn.rebrickable.com/media/sets/10309-1/126868.jpg"},
                {"set_name": "Orchid", "set_number": "10311", "theme": "Botanicals", "purchase_price": 49.99, "quantity": 1, "condition": "New", "year": 2022, "num_parts": 608, "image_url": "https://cdn.rebrickable.com/media/sets/10311-1/126896.jpg"},
            ]
            for s in demo_sets:
                db.add(model.LegoSet(**s))
            db.commit()
    finally:
        db.close()

seed_if_empty()

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello Xiaoqi! Your Lego API is alive!"}

@app.get("/sets")
def get_all_sets():
    db = SessionLocal()
    try:
        # add one final "View" button
        all_sets = db.query(model.LegoSet).all()
        return all_sets
    finally:
        db.close()

@app.post("/add-set")
def create_set(lego_set: schemas.LegoSet):
    db = SessionLocal()
    try:
        # 1. CHECK: Does this set_number already exist in our database?
        existing_set = db.query(model.LegoSet).filter(model.LegoSet.set_number == lego_set.set_number).first()

        if existing_set:
            # 2. REJECT: Tell the user exactly why we won't add it
            raise HTTPException(status_code=400, detail=f"Set {lego_set.set_number} is already in your collection!")

        # 3. PROCEED: If it's unique, save it
        db_set = model.LegoSet(**lego_set.dict())
        db.add(db_set)
        db.commit()
        return {"message": f"Successfully added {lego_set.set_name}!"}
    finally:
        db.close()

@app.get("/portfolio/stats")
def get_portfolio_stats():
    db = SessionLocal()
    try:
        sets = db.query(model.LegoSet).all()

        total_spent = 0
        total_value = 0

        for s in sets:
            # Multiply by quantity to get the true total
            total_spent += (s.purchase_price * s.quantity)
            current_price = market.get_market_price(s.set_number)
            total_value += (current_price * s.quantity)

        profit = total_value - total_spent
        roi = (profit / total_spent * 100) if total_spent > 0 else 0

        return {
            "user": "Xiaoqi Jiang",
            "total_sets": len(sets),
            "summary": {
                "total_investment": f"${total_spent:,.2f}",
                "current_market_value": f"${total_value:,.2f}",
                "net_profit": f"${profit:,.2f}",
                "roi_percentage": f"{roi:.2f}%"
            },
            "note": "Market data currently provided by Mock Service"
        }
    finally:
        db.close()

@app.get("/portfolio/history")
def get_price_history():
    db = SessionLocal()
    try:
        history = db.query(model.PriceHistory).order_by(model.PriceHistory.captured_at).all()
        return history
    finally:
        db.close()

@app.get("/lookup-set/{set_number}")
def lookup_set(set_number: str):
    url = f"https://rebrickable.com/api/v3/lego/sets/{set_number}-1/"
    response = requests.get(url, headers=REBRICKABLE_HEADERS)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Set {set_number} not found in Rebrickable")

    details = response.json()

    theme_url = f"https://rebrickable.com/api/v3/lego/themes/{details['theme_id']}/"
    theme_response = requests.get(theme_url, headers=REBRICKABLE_HEADERS)
    theme_name = theme_response.json().get("name", "Unknown") if theme_response.status_code == 200 else "Unknown"

    return {
        "set_name": details["name"],
        "theme": theme_name,
        "year": details.get("year"),
        "num_parts": details.get("num_parts"),
        "image_url": details.get("set_img_url")
    }