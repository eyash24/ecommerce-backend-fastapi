from pydantic import BaseModel, ConfigDict

class WishlistBase(BaseModel):
    product_id: int

class WishlistCreate(WishlistBase):
    pass

class WishlistResponse(WishlistBase):
    model_config = ConfigDict()
    id: int
    user_id: int
    product_id: int

