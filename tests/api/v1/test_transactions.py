from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.config import settings
from app.models.book import Book as ModelBook
from app.crud import crud_book
from app.models.user import User

def create_test_book_for_transaction(db: Session, client: TestClient, headers: dict) -> ModelBook:
    book_data = {"title": "Transaction Test Book", "author": "Trans Author", "isbn": "5555555555555", "total_quantity": 2}
    response = client.post(f"{settings.API_V1_STR}/books/", json=book_data, headers=headers)
    assert response.status_code == 201
    book_id = response.json()["id"]
    book = crud_book.get_book(db, book_id)
    assert book is not None
    return book


def test_lend_book(client: TestClient, db: Session, auth_token_headers: dict, test_user: User):
    book = create_test_book_for_transaction(db, client, auth_token_headers)
    initial_available = book.available_quantity

    transaction_data = {"book_id": book.id}
    response = client.post(f"{settings.API_V1_STR}/transactions/give", json=transaction_data, headers=auth_token_headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["transaction_type"] == "lend"
    assert data["book_id"] == book.id
    assert data["user_id"] == test_user.id

    db.refresh(book)
    assert book.available_quantity == initial_available - 1

    response_no_auth = client.post(f"{settings.API_V1_STR}/transactions/give", json=transaction_data)
    assert response_no_auth.status_code == 401
    
    client.post(f"{settings.API_V1_STR}/transactions/give", json=transaction_data, headers=auth_token_headers)
    db.refresh(book)
    assert book.available_quantity == initial_available - 2
    
    response_unavailable = client.post(f"{settings.API_V1_STR}/transactions/give", json=transaction_data, headers=auth_token_headers)
    assert response_unavailable.status_code == 400

def test_return_book(client: TestClient, db: Session, auth_token_headers: dict, test_user: User):
    book = create_test_book_for_transaction(db, client, auth_token_headers)
    
    lend_data = {"book_id": book.id}
    client.post(f"{settings.API_V1_STR}/transactions/give", json=lend_data, headers=auth_token_headers)
    db.refresh(book)
    available_after_lend = book.available_quantity

    return_data = {"book_id": book.id}
    response = client.post(f"{settings.API_V1_STR}/transactions/take", json=return_data, headers=auth_token_headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["transaction_type"] == "return"
    assert data["book_id"] == book.id
    assert data["user_id"] == test_user.id

    db.refresh(book)
    assert book.available_quantity == available_after_lend + 1

    response_no_auth = client.post(f"{settings.API_V1_STR}/transactions/take", json=return_data)
    assert response_no_auth.status_code == 401
    
    fresh_book_data = {"title": "Fresh Book", "author": "Fresh Author", "isbn": "6666666666666", "total_quantity": 1}
    fresh_book_resp = client.post(f"{settings.API_V1_STR}/books/", json=fresh_book_data, headers=auth_token_headers)
    fresh_book_id = fresh_book_resp.json()["id"]
    fresh_book = crud_book.get_book(db, fresh_book_id)
    assert fresh_book is not None
    assert fresh_book.available_quantity == fresh_book.total_quantity

    return_fresh_data = {"book_id": fresh_book.id}
    response_return_fresh = client.post(f"{settings.API_V1_STR}/transactions/take", json=return_fresh_data, headers=auth_token_headers)
    assert response_return_fresh.status_code == 201
    db.refresh(fresh_book)
    assert fresh_book.available_quantity == fresh_book.total_quantity

def test_list_transactions(client: TestClient, db: Session, auth_token_headers: dict, test_user: User):
    book = create_test_book_for_transaction(db, client, auth_token_headers)
    
    client.post(f"{settings.API_V1_STR}/transactions/give", json={"book_id": book.id}, headers=auth_token_headers)
    client.post(f"{settings.API_V1_STR}/transactions/take", json={"book_id": book.id}, headers=auth_token_headers)

    response = client.get(f"{settings.API_V1_STR}/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    response_user_filter = client.get(f"{settings.API_V1_STR}/transactions/?user_id={test_user.id}")
    assert response_user_filter.status_code == 200
    assert all(t['user_id'] == test_user.id for t in response_user_filter.json())

    response_book_filter = client.get(f"{settings.API_V1_STR}/transactions/?book_id={book.id}")
    assert response_book_filter.status_code == 200
    assert all(t['book_id'] == book.id for t in response_book_filter.json())