# app/models.py

from pydantic import BaseModel, Field
from datetime import datetime

class PriceDataIn(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

class PriceDataOut(PriceDataIn):
    """Add extra fields if you want to expose them on GET /data."""
    pass
