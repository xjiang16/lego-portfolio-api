from pydantic import BaseModel, Field
from typing import Optional

# Define what data we accept

class LegoSet(BaseModel):
    set_name: str
    set_number: str
    theme: str
    purchase_price: float = Field(gt=0)
    quantity: int = Field(gt=0)
    estimated_market_value: float
    condition: str
    is_sealed: bool
    notes: str
    year: Optional[int] = None
    num_parts: Optional[int] = None
    image_url: Optional[str] = None