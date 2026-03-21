from fastapi import FastAPI
from schemas import LegoSet

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello Xiaoqi! Your Lego API is alive!"}

@app.post("/add-set")
def create_set(item: LegoSet):
    return {"status": "Success", "added_item": item}