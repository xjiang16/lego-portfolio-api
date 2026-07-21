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
    loaded_count = 0
    skipped_count = 0
    try:
        for item in cleaned_data:
            existing = db.query(model.LegoSet).filter(
                model.LegoSet.set_number == item["set_number"]
            ).first()

            if existing:
                skipped_count += 1
                continue

            new_set = model.LegoSet(**item)
            db.add(new_set)
            loaded_count += 1

        db.commit()
        print(f"Loaded {loaded_count} new sets, skipped {skipped_count} duplicates.")

    except Exception as e:
        print(f"Error loading to DB: {e}")
        db.rollback()

    finally:
        db.close()

# --- THE TRIGGER ---
if __name__ == "__main__":
    print("Starting ETL Pipeline...")
    cleaned = clean_data(raw_lego_data)
    load_to_db(cleaned)