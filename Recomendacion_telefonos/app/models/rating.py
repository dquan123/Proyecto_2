from pydantic import BaseModel

class Rating(BaseModel):
    user_id: str
    phone_id: str
    stars: int  # 0 a 5
