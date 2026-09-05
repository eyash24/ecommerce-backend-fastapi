from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# orderManage
class OrderManageBase(BaseModel):
    items: int
    total_price: float
    payment_status: bool
    user_id: int

class OrderManageCreate(OrderManageBase):
    pass

class OrderManageUpdate(BaseModel):
    items: int | None = Field(default=None)
    total_price: float | None = Field(default=None)
    payment_status: bool | None = Field(default=None)

class OrderManageIDResponse(OrderManageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

# order 
class OrderBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    product_id: int | None = Field(default=None)
    quantity: int | None = Field(default=None)

class OrderIDResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int

