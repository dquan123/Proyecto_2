from pydantic import BaseModel
from typing import List

class Phone(BaseModel):
    id: str
    name: str
    brand: str
    storage: int
    screen_size: float
    camera_quality: str
    battery_life: str
    design_size: str
    price: float
    software: str
