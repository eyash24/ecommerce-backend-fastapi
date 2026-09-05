from pydantic import BaseModel, ConfigDict, Field

class CartBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    product_id: int | None = Field(default=None)
    quantity: int | None = Field(default=None)

class CartIDResponse(CartBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

