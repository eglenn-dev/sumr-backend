from fastapi import APIRouter
from app.api.v1.endpoints import auth, books, transactions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Users"])
api_router.include_router(books.router, prefix="/books", tags=["Book Management"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])