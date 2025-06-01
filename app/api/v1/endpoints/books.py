from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api import deps
from app.crud import crud_book
from app.models.user import User
from app.models.book import Book as ModelBook
from app.schemas import book as book_schema
from app.schemas import msg as msg_schema


router = APIRouter()

@router.post("/", response_model=book_schema.BookRead, status_code=status.HTTP_201_CREATED)
def create_book(
    *,
    db: Session = Depends(deps.get_db),
    book_in: book_schema.BookCreate,
    current_user: User = Depends(deps.get_current_active_user) # Protected
):
    """
    Add a new book. (Protected)
    """    
    return crud_book.create_book(db=db, book_in=book_in)

@router.get("/", response_model=List[book_schema.BookRead])
def list_books(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    title: Optional[str] = Query(None, min_length=1, max_length=50),
    author: Optional[str] = Query(None, min_length=1, max_length=50)
):
    """
    List all books with pagination and filtering. (Public)
    """
    books = crud_book.get_books(db=db, skip=skip, limit=limit, title=title, author=author)
    return books

@router.get("/{book_id}", response_model=book_schema.BookRead)
def read_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int,
):
    """
    Get a specific book by ID. (Public - not specified but good to have)
    """
    db_book = crud_book.get_book(db=db, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return db_book


@router.delete("/{book_id}", response_model=msg_schema.Msg)
def remove_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int,
    current_user: User = Depends(deps.get_current_active_user) # Protected
):
    """
    Remove a book. (Protected)
    """
    book_to_delete = crud_book.get_book(db=db, book_id=book_id)
    if not book_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    crud_book.delete_book(db=db, book_id=book_id)
    return {"message": f"Book with ID {book_id} removed successfully"}

@router.put("/{book_id}", response_model=book_schema.BookRead)
def update_book_details(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int,
    book_in: book_schema.BookUpdate,
    current_user: User = Depends(deps.get_current_active_user)
):
    db_book = crud_book.get_book(db=db, book_id=book_id)
    if not db_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    updated_book = crud_book.update_book(db=db, db_book=db_book, book_in=book_in)
    return updated_book