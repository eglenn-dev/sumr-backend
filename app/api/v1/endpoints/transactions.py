from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api import deps
from app.crud import crud_transaction, crud_book
from app.models.user import User
from app.models.transaction import TransactionType
from app.schemas import transaction as transaction_schema
from app.schemas import msg as msg_schema

router = APIRouter()

@router.post("/give", response_model=transaction_schema.TransactionRead, status_code=status.HTTP_201_CREATED)
def lend_book_to_user(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: transaction_schema.TransactionCreateGive,
    current_user: User = Depends(deps.get_current_active_user) # Protected
):
    """
    Lend a book to the current authenticated user. (Protected)
    """
    book = crud_book.get_book(db=db, book_id=transaction_in.book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    
    if book.available_quantity <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book is not available for lending")

    try:
        transaction = crud_transaction.create_transaction(
            db=db,
            book=book,
            user=current_user,
            transaction_type=TransactionType.LEND
        )
        db.refresh(transaction, attribute_names=['book', 'user'])
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/take", response_model=transaction_schema.TransactionRead, status_code=status.HTTP_201_CREATED)
def return_book_from_user(
    *,
    db: Session = Depends(deps.get_db),
    transaction_in: transaction_schema.TransactionCreateTake,
    current_user: User = Depends(deps.get_current_active_user) # Protected
):
    """
    Return a book from the current authenticated user. (Protected)
    """
    book = crud_book.get_book(db=db, book_id=transaction_in.book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if book.available_quantity >= book.total_quantity:
         pass

    try:
        transaction = crud_transaction.create_transaction(
            db=db,
            book=book,
            user=current_user,
            transaction_type=TransactionType.RETURN
        )
        db.refresh(transaction, attribute_names=['book', 'user'])
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[transaction_schema.TransactionRead])
def list_transactions(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    book_id: Optional[int] = Query(None, description="Filter by book ID")
):
    """
    List all transactions. (Public)
    Allows filtering by user_id or book_id.
    """
    transactions = crud_transaction.get_transactions(db=db, skip=skip, limit=limit, user_id=user_id, book_id=book_id)
    for t in transactions:
        db.refresh(t, attribute_names=['book', 'user'])
    return transactions