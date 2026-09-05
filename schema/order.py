from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# orderManage
class OrderManageBase(BaseModel):
    items: int
    total_price: float
    payment_status: bool
    payment_mode: str = Field(min_length=2, max_length=15)
    shipping_id: int

class OrderManageCreate(OrderManageBase):
    pass

class OrderManageUpdate(BaseModel):
    items: int | None = Field(default=None)
    total_price: float | None = Field(default=None)
    payment_status: bool | None = Field(default=None)
    payment_mode: str | None = Field(default=None, min_length=2, max_length=15)
    shipping_id: int | None = Field(default=None)

class OrderManageIDResponse(OrderManageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    user_id: int

# order 
class OrderBase(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    quantity: int | None = Field(default=None)

class OrderIDResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    order_manage_id: int

