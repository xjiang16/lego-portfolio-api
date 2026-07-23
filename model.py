from database import Base
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime

class LegoSet(Base):
    __tablename__ = "lego_sets"

    id = Column(Integer, primary_key=True, index=True)
    set_name = Column(String, unique=True)
    set_number = Column(String, unique=True)
    theme = Column(String)
    purchase_price = Column(Float)
    quantity = Column(Integer)
    estimated_market_value = Column(Float, nullable=True)
    condition = Column(String)
    is_sealed = Column(Boolean, default=True)
    notes = Column(String, nullable=True)
    year = Column(Integer, nullable=True) 
    num_parts = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    set_number = Column(String, index=True)
    price = Column(Float)
    captured_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))