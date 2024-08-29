from pydantic import BaseModel

# Pydantic schemas 
class PinSchema(BaseModel):
    latitude: float
    longitude: float
    title: str
    details: str
    user_id: int