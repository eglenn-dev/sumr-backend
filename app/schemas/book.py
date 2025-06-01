from pydantic import BaseModel, Field
from typing import Optional

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    isbn: str = Field(..., min_length=10, max_length=20)
    total_quantity: int = Field(..., gt=0)

class BookCreate(BookBase):
    pass

class BookRead(BookBase):
    id: int
    available_quantity: int

    class Config:
        from_attributes = True

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)