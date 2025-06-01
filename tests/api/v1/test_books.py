from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.config import settings
from app.models.book import Book as ModelBook

def test_create_book(client: TestClient, db: Session, auth_token_headers: dict):
    book_data = {"title": "Test Book 1", "author": "Test Author 1", "isbn": "1234567890123", "total_quantity": 10}
    response = client.post(f"{settings.API_V1_STR}/books/", json=book_data, headers=auth_token_headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["available_quantity"] == book_data["total_quantity"]
    assert "id" in data

    response_no_auth = client.post(f"{settings.API_V1_STR}/books/", json=book_data)
    assert response_no_auth.status_code == 401


def test_list_books(client: TestClient, db: Session, auth_token_headers: dict):
    book_data = {"title": "Listable Book", "author": "List Author", "isbn": "9876543210987", "total_quantity": 5}
    client.post(f"{settings.API_V1_STR}/books/", json=book_data, headers=auth_token_headers)

    response = client.get(f"{settings.API_V1_STR}/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(b['title'] == "Listable Book" for b in data)

    # Test pagination
    response_limit = client.get(f"{settings.API_V1_STR}/books/?limit=1")
    assert response_limit.status_code == 200
    assert len(response_limit.json()) <= 1

    # Test filtering
    response_filter = client.get(f"{settings.API_V1_STR}/books/?title=Listable")
    assert response_filter.status_code == 200
    assert len(response_filter.json()) > 0
    assert all("Listable" in b['title'] for b in response_filter.json())


def test_get_book(client: TestClient, db: Session, auth_token_headers: dict):
    book_data = {"title": "Specific Book", "author": "Specific Author", "isbn": "1122334455667", "total_quantity": 3}
    create_response = client.post(f"{settings.API_V1_STR}/books/", json=book_data, headers=auth_token_headers)
    book_id = create_response.json()["id"]

    response = client.get(f"{settings.API_V1_STR}/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["id"] == book_id

    response_not_found = client.get(f"{settings.API_V1_STR}/books/99999")
    assert response_not_found.status_code == 404


def test_delete_book(client: TestClient, db: Session, auth_token_headers: dict):
    book_data = {"title": "Deletable Book", "author": "Delete Author", "isbn": "0011223344556", "total_quantity": 1}
    create_response = client.post(f"{settings.API_V1_STR}/books/", json=book_data, headers=auth_token_headers)
    book_id = create_response.json()["id"]

    delete_response = client.delete(f"{settings.API_V1_STR}/books/{book_id}", headers=auth_token_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Book with ID {book_id} removed successfully"

    get_response = client.get(f"{settings.API_V1_STR}/books/{book_id}")
    assert get_response.status_code == 404

    create_response_again = client.post(f"{settings.API_V1_STR}/books/", json=book_data, headers=auth_token_headers)
    book_id_again = create_response_again.json()["id"]
    delete_no_auth = client.delete(f"{settings.API_V1_STR}/books/{book_id_again}")
    assert delete_no_auth.status_code == 401