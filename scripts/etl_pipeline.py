import sys
import os
import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import model

load_dotenv()
API_KEY = os.getenv("REBRICKABLE_API_KEY")
HEADERS = {"Authorization": f"key {API_KEY}"}

# --- PHASE 1: EXTRACT ---
# My "shopping list" — sets you own + what I paid.
# Rebrickable fills in the rest (name, theme, etc) since it doesn't know my purchase price.
my_sets = [
    {"set_number": "10329", "purchase_price": 49.99, "quantity": 1},
    {"set_number": "10309", "purchase_price": 44.99, "quantity": 1},
    {"set_number": "10311", "purchase_price": 49.99, "quantity": 1},
]

def fetch_set_details(set_number):
    """Calls Rebrickable for real catalog data on one set."""
    url = f"https://rebrickable.com/api/v3/lego/sets/{set_number}-1/"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"Could not fetch {set_number}: status {response.status_code}")
        return None

    return response.json()


def fetch_theme_name(theme_id):
    """Rebrickable only gives us a numeric theme_id — resolve it to a real name."""
    url = f"https://rebrickable.com/api/v3/lego/themes/{theme_id}/"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return "Unknown"

    return response.json().get("name", "Unknown")


# --- PHASE 2: TRANSFORM ---
def build_cleaned_data(shopping_list):
    cleaned_items = []

    for item in shopping_list:
        details = fetch_set_details(item["set_number"])

        if details is None:
            continue  

        theme_name = fetch_theme_name(details["theme_id"])
        print(f"{item['set_number']} -> {details['name']} | theme: {theme_name}")  

        cleaned_items.append({
            "set_name": details["name"],
            "set_number": item["set_number"],
            "purchase_price": item["purchase_price"],
            "theme": theme_name,
            "quantity": item["quantity"],
            "condition": "New",
            "year": details.get("year"),
            "num_parts": details.get("num_parts"),
            "image_url": details.get("set_img_url"),
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
    print("Starting ETL Pipeline (Rebrickable-powered)...")
    cleaned = build_cleaned_data(my_sets)
    load_to_db(cleaned)