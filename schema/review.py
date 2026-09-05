from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ReviewBase(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    rating: float
    comment: str = Field(max_length=250)
    user_id: int
    product_id: int

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    title: str = Field(default=None, min_length=1, max_length=50)
    rating: float = Field(default=None)
    comment: str = Field(default=None, max_length=250)

class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

