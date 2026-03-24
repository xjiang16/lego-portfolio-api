from fastapi import FastAPI
import model
from database import engine
from schemas import LegoSet

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello Xiaoqi! Your Lego API is alive!"}

@app.post("/add-set")
def create_set(item: LegoSet):
    return {"status": "Success", "added_item": item}

@app.get("/sets")
def get_all_sets():
    db = SessionLocal()
    try:
        # add one final "View" button
        all_sets = db.query(model.LegoSet).all()
        return all_sets
    finally:
        db.close()