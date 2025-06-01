from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from typing import Optional
from .user import User
from .book import Book

class TransactionType(str, Enum):
    LEND = "lend"
    RETURN = "return"

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    transaction_type: TransactionType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    book_id: int = Field(foreign_key="book.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    user: Optional["User"] = Relationship(back_populates="transactions")
    book: Optional["Book"] = Relationship(back_populates="transactions")