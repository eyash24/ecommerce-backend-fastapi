from pydantic import BaseModel, ConfigDict, Field
from .product import ProductResponse
from datetime import datetime

class CartBase(BaseModel):
    product_id: int
    quantity: int

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    quantity: int | None = Field(default=None)

class CartIDResponse(CartBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    user_id: int

class CartProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product: ProductResponse
    quantity: int
    created_at: datetime
    user_id: int
