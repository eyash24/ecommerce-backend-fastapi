from pydantic import BaseModel, ConfigDict
from datetime import datetime

class WishlistBase(BaseModel):
    product_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistResponse(WishlistBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    product_id: int
    created_at: datetime

