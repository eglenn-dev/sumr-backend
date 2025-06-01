from pydantic import BaseModel
from datetime import datetime
from app.models.transaction import TransactionType
from app.schemas.user import UserRead 
from app.schemas.book import BookRead
from typing import Optional


class TransactionBase(BaseModel):
    book_id: int

class TransactionCreateGive(BaseModel):
    book_id: int

class TransactionCreateTake(BaseModel):
    book_id: int

class TransactionRead(BaseModel):
    id: int
    transaction_type: TransactionType
    timestamp: datetime
    book_id: int
    user_id: int
    
    book: Optional[BookRead] = None
    user: Optional[UserRead] = None

    class Config:
        from_attributes = True