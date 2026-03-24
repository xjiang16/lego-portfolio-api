from database import Base
from sqlalchemy import Column, Integer, String, Float, Boolean

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