from sqlmodel import Session, select
from typing import List, Optional

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate

def get_book(db: Session, book_id: int) -> Optional[Book]:
    return db.get(Book, book_id)

def get_books(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    title: Optional[str] = None, 
    author: Optional[str] = None
) -> List[Book]:
    statement = select(Book)
    if title:
        statement = statement.where(Book.title.ilike(f"%{title}%"))
    if author:
        statement = statement.where(Book.author.ilike(f"%{author}%"))
    statement = statement.offset(skip).limit(limit)
    return db.exec(statement).all()

def create_book(db: Session, book_in: BookCreate) -> Book:
    db_book = Book(
        **book_in.model_dump(),
        available_quantity=book_in.total_quantity
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, db_book: Book, book_in: BookUpdate) -> Book:
    book_data = book_in.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
    
def delete_book(db: Session, book_id: int) -> Optional[Book]:
    db_book = db.get(Book, book_id)
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book

def update_book_availability(db: Session, book_id: int, change: int) -> Optional[Book]:
    """
    Updates the available quantity of a book.
    `change` can be positive (returning a book) or negative (lending a book).
    """
    db_book = db.get(Book, book_id)
    if not db_book:
        return None

    new_available_quantity = db_book.available_quantity + change
    
    if new_available_quantity < 0:
        raise ValueError("Available quantity cannot be negative.")
    if new_available_quantity > db_book.total_quantity:
        new_available_quantity = db_book.total_quantity
        
    db_book.available_quantity = new_available_quantity
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book