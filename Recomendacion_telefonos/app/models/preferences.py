from pydantic import BaseModel

class Preferences(BaseModel):
    user_id: str
    preferred_storage: int
    preferred_screen_size: float
    preferred_camera: str
    preferred_battery: str
    preferred_design: str
    preferred_price_range: str  # ej. "low", "medium", "high"
    preferred_software: str
