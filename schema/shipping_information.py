from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# shipping information
class ShippingInformatinBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(max_length=50)
    address: str = Field(min_length=10, max_length=250)
    city: str = Field(max_length=50)
    state: str = Field(max_length=50)
    zip: str = Field(max_length=10)

class ShippingInformationCreate(ShippingInformatinBase):
    pass

class ShippingInformatinUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, min_length=10, max_length=250)
    city: str | None = Field(default=None, max_length=50)
    state: str | None = Field(default=None, max_length=50)
    zip: str | None = Field(default=None, max_length=10)

class ShippingInformationResponse(ShippingInformatinBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
