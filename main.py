from fastapi import FastAPI
from fastapi import HTTPException
import model
from database import engine, SessionLocal
import schemas
from schemas import LegoSet

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

        total_count = len(sets)
        # Summing up what you actually paid
        total_investment = sum(s.purchase_price for s in sets if s.purchase_price)

        return {
            "user": "Xiaoqi Jiang",
            "total_sets_owned": total_count,
            "total_capital_invested": f"${total_investment:,.2f}",
            "status": "Awaiting Live Market Data from eBay"
        }
    finally:
        db.close()