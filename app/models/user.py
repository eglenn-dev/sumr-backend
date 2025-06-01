from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = Field(default=None, max_length=100)
    hashed_password: str
    is_active: bool = Field(default=True)

    transactions: List["Transaction"] = Relationship(back_populates="user")