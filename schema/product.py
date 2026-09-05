from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str = Field(max_length=500)
    price: float 
    image_url: str = Field(max_length=200)
    category: str = Field(max_length=50)
    owner_id: int
    quantity: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None)
    image_url: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=50)
    quantity: int | None = Field(default=None)

class ProductStockStatus(BaseModel):
    inStock: bool 


class PaginatedProductResponse(BaseModel):
    products: list[ProductResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
