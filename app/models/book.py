from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(index=True, max_length=200)
    author: str = Field(index=True, max_length=100)
    isbn: str = Field(unique=True, index=True, max_length=20)
    total_quantity: int = Field(gt=0)
    available_quantity: int 

    transactions: List["Transaction"] = Relationship(back_populates="book")