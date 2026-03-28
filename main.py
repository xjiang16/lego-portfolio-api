from fastapi import FastAPI
from fastapi import HTTPException
import model
from database import engine, SessionLocal
import schemas
from services import market

model.Base.metadata.create_all(bind=engine)

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