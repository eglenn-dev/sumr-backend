from sqlmodel import Session, select
from typing import List, Optional

from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.models.book import Book
from app.crud import crud_book

def create_transaction(
    db: Session, 
    *, 
    book: Book, 
    user: User, 
    transaction_type: TransactionType
) -> Transaction:
    
    if transaction_type == TransactionType.LEND:
        if book.available_quantity <= 0:
            raise ValueError("Book not available for lending")
        crud_book.update_book_availability(db=db, book_id=book.id, change=-1)
    elif transaction_type == TransactionType.RETURN:
        crud_book.update_book_availability(db=db, book_id=book.id, change=1)
    
    db.refresh(book)

    db_transaction = Transaction(
        book_id=book.id,
        user_id=user.id,
        transaction_type=transaction_type
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_transactions(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None, book_id: Optional[int] = None) -> List[Transaction]:
    statement = select(Transaction).order_by(Transaction.timestamp.desc())
    if user_id:
        statement = statement.where(Transaction.user_id == user_id)
    if book_id:
        statement = statement.where(Transaction.book_id == book_id)
    
    statement = statement.offset(skip).limit(limit)
    transactions = db.exec(statement).all()
    return transactions

def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.get(Transaction, transaction_id)