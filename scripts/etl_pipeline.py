import sys
import os

# 1. THE CONNECTION: This tells Python to look outside the 'scripts' folder so it can find the database.py and models.py files.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import model

# --- PHASE 1: EXTRACT ---
raw_lego_data = [
    {"name": "Tiny Plants", "number": "10329", "price": "$49.99"},
    {"name": "Succulents", "number": "10309", "price": "44.99 USD"},
    {"name": "Orchid", "number": "10311", "price": "49.99"},
]

# --- PHASE 2: TRANSFORM ---
def clean_data(raw_list):
    cleaned_items = []
    for item in raw_list:
        raw_price = str(item.get("price", "0"))
        clean_price = float(raw_price.replace("$", "").replace("USD", "").strip())

        cleaned_items.append({
            "set_name": item.get("name"),
            "set_number": item.get("number"),
            "purchase_price": clean_price,
            "theme": "Botanical",
            "quantity": 1,
            "condition": "New"
        })

    return cleaned_items

# --- PHASE 3: LOAD ---
def load_to_db(cleaned_data):
    db = SessionLocal()
    try:
        for item in cleaned_data:
        # Create a 'Model' object for the database
            new_set = model.LegoSet(**item)
            db.add(new_set)

        db.commit()
        print(f"Successfully loaded {len(cleaned_data)} sets!")

    except Exception as e:
        print(f"Error loading to DB: {e}")
        db.rollback()
        # If it fails, don't save half-finished data

    finally:
        db.close()

# --- THE TRIGGER ---
if __name__ == "__main__":
    print(f"Columns in LegoSet: {model.LegoSet.__table__.columns.keys()}")
    print("Starting ETL Pipeline...")
    cleaned = clean_data(raw_lego_data)
    load_to_db(cleaned)