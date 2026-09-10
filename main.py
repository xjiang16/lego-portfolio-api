from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session

import model
from database import engine, SessionLocal, get_db
import schemas
from services import market
import os
import requests
from dotenv import load_dotenv

load_dotenv()
REBRICKABLE_API_KEY = os.getenv("REBRICKABLE_API_KEY")
REBRICKABLE_HEADERS = {"Authorization": f"key {REBRICKABLE_API_KEY}"}


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    model.Base.metadata.create_all(bind=engine)
    # Tests set SEED_DEMO_DATA=false so they start from a clean, empty DB.
    if os.getenv("SEED_DEMO_DATA", "true").lower() != "false":
        seed_if_empty()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Hello Xiaoqi! Your Lego API is alive!"}

@app.get("/sets")
def get_all_sets(db: Session = Depends(get_db)):
    # add one final "View" button
    all_sets = db.query(model.LegoSet).all()
    return all_sets

@app.post("/add-set")
def create_set(lego_set: schemas.LegoSet, db: Session = Depends(get_db)):
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

@app.delete("/sets/{set_id}")
def delete_set(set_id: int, db: Session = Depends(get_db)):
    db_set = db.query(model.LegoSet).filter(model.LegoSet.id == set_id).first()

    if not db_set:
        raise HTTPException(status_code=404, detail=f"Set with id {set_id} not found")

    db.delete(db_set)
    db.commit()
    return {"message": f"Successfully deleted {db_set.set_name}"}

def _compute_portfolio_totals(db: Session):
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
        # Total physical sets owned, not just distinct rows — a row with quantity=3 counts as 3.
        "total_sets": sum(s.quantity for s in sets),
        "total_spent": total_spent,
        "total_value": total_value,
        "profit": profit,
        "roi": roi,
    }


@app.get("/portfolio/stats")
def get_portfolio_stats(db: Session = Depends(get_db)):
    totals = _compute_portfolio_totals(db)

    return {
        "user": "Xiaoqi Jiang",
        "total_sets": totals["total_sets"],
        "summary": {
            "total_investment": f"${totals['total_spent']:,.2f}",
            "current_market_value": f"${totals['total_value']:,.2f}",
            "net_profit": f"${totals['profit']:,.2f}",
            "roi_percentage": f"{totals['roi']:.2f}%"
        },
        "note": "Market data currently provided by Mock Service"
    }

def _badge_svg(label: str, value: str, color: str) -> str:
    """Renders a shields.io-style badge: a gray label chip next to a colored value chip."""
    label_width = int(len(label) * 6.5) + 20
    value_width = int(len(value) * 6.5) + 20
    total_width = label_width + value_width

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_width / 2}" y="14">{label}</text>
    <text x="{label_width + value_width / 2}" y="14">{value}</text>
  </g>
</svg>'''


@app.get("/badge/roi.svg")
def roi_badge(db: Session = Depends(get_db)):
    totals = _compute_portfolio_totals(db)

    if totals["total_spent"] <= 0:
        value, color = "n/a", "#9f9f9f"  # gray — nothing invested yet, distinct from a 0% ROI
    else:
        roi = totals["roi"]
        value = f"{roi:+.1f}%"
        color = "#4c1" if roi >= 0 else "#e05d44"  # green / red, shields.io's brightgreen & red

    svg = _badge_svg("LEGO ROI", value, color)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@app.get("/portfolio/history")
def get_price_history(db: Session = Depends(get_db)):
    history = db.query(model.PriceHistory).order_by(model.PriceHistory.captured_at).all()
    return history

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