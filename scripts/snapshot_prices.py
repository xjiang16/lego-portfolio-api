import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import model
from services import market

def take_snapshot():
    db = SessionLocal()
    try:
        all_sets = db.query(model.LegoSet).all()
        snapshot_count = 0

        for lego_set in all_sets:
            current_price = market.get_market_price(lego_set.set_number)

            snapshot = model.PriceHistory(
                set_number=lego_set.set_number,
                price=current_price
            )
            db.add(snapshot)
            snapshot_count += 1

        db.commit()
        print(f"Captured {snapshot_count} price snapshots.")

    except Exception as e:
        print(f"Error taking snapshot: {e}")
        db.rollback()

    finally:
        db.close()

if __name__ == "__main__":
    print("Taking price snapshot...")
    take_snapshot()