from pydantic import BaseModel
from typing import Optional

# Define what data we accept

class LegoSet(BaseModel):
    set_name: str
    set_number: str
    theme: str
    purchase_price: float
    quantity: int
    estimated_market_value: float
    condition: str
    is_sealed: bool
    notes: str

