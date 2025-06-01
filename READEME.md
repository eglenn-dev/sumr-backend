# Inventory Management System API

A REST API for managing a book inventory system, built with FastAPI and PostgreSQL.
This project allows users to manage books, and lend/return them, with JWT-based authentication for protected operations.

**Duration**: 5-7 days

**Level**: Intermediate

**Tech Stack**: FastAPI, PostgreSQL, SQLModel, Alembic, Pytest, Docker, JWT

## Objective

Build a fully functional REST API for an Inventory Management System that manages books. The system supports operations like adding, deleting, lending, and returning books—with authentication, pagination, and full test coverage.

## Features

-   **User Management**:
    -   User creation (`POST /api/v1/users/`)
    -   User login to obtain JWT (`POST /api/v1/auth/login/token`)
    -   Get current user details (`GET /api/v1/users/me`)
-   **Book Management**:
    -   Add a new book (`POST /api/v1/books/`) - Protected
    -   List all books with pagination and filtering (`GET /api/v1/books/`) - Public
    -   Get a specific book by ID (`GET /api/v1/books/{book_id}`) - Public
    -   Remove a book (`DELETE /api/v1/books/{book_id}`) - Protected
-   **Transactions**:
    -   Lend a book to an authenticated user (`POST /api/v1/transactions/give`) - Protected
    -   Return a book from an authenticated user (`POST /api/v1/transactions/take`) - Protected
    -   List all transactions with pagination (`GET /api/v1/transactions/`) - Public
-   **Authentication**:
    -   JWT-based authentication for protected routes.
-   **Database**:
    -   PostgreSQL backend.
    -   SQLModel for ORM and data validation.
    -   Alembic for database migrations.
-   **Containerization**:
    -   Docker and Docker Compose for easy setup and deployment.
-   **Testing**:
    -   Unit tests with Pytest.

## Project Structure

```

.
├── alembic/ # Alembic migration scripts
├── app/ # Main application code
│ ├── api/ # API routers and dependencies
│ ├── core/ # Configuration and security
│ ├── crud/ # CRUD operations
│ ├── db/ # Database session and base
│ ├── models/ # SQLModel table definitions
│ ├── schemas/ # Pydantic schemas for API I/O
│ └── main.py # FastAPI application entrypoint
├── tests/ # Pytest tests
├── .env.example # Environment variable template
├── .gitignore
├── alembic.ini # Alembic configuration
├── docker-compose.yml # Docker Compose setup
├── Dockerfile # Dockerfile for the API service
├── README.md
└── requirements.txt # Python dependencies

```

## Setup Instructions

### Prerequisites

-   Docker and Docker Compose
-   Python 3.9+ (for local development if not using Docker exclusively)
-   Git

### 1. Clone the Repository

```bash
git clone <repository_url>
cd inventory_management_fastapi
```

### 2. Configure Environment Variables

Copy the example environment file and customize it if needed:

```bash
cp .env.example .env
```

The default `.env` values are configured to work with the `docker-compose.yml` setup.
Key variables:

-   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Credentials for the PostgreSQL container.
-   `SECRET_KEY`: A secret key for JWT token generation. **Change this in a production environment!**
-   `LOCAL_DATABASE_URL`: Used by Alembic when running migrations locally (outside Docker). Ensure this matches your local PostgreSQL setup if you intend to run Alembic this way.

### 3. Build and Run with Docker Compose

This is the recommended way to run the application and database:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.
The OpenAPI documentation (Swagger UI) will be at `http://localhost:8000/api/v1/docs`.
The ReDoc documentation will be at `http://localhost:8000/api/v1/redoc`.

### 4. Apply Database Migrations (First Time or After Model Changes)

Migrations should ideally be applied automatically or as a separate step in a deployment pipeline. For local development with Docker Compose, you can run migrations by exec-ing into the `api` container after it's up and running (or before starting the app if the app fails due to missing tables).

**Method 1: Exec into the running `api` container:**

```bash
docker-compose exec api alembic upgrade head
```

**Method 2: Run Alembic locally (requires local Python env and `psycopg2-binary`)**
Ensure your local PostgreSQL server is running (or the one from docker-compose is accessible on `localhost:5432` and `LOCAL_DATABASE_URL` in `.env` is set correctly).

```bash
# Install requirements if not already: pip install -r requirements.txt
# Ensure LOCAL_DATABASE_URL in .env points to your accessible PostgreSQL
alembic upgrade head
```

_Note_: The `docker-compose.yml` doesn't automatically run migrations. You'll need to do this manually the first time or when models change. A production setup might include this in an entrypoint script.

## API Endpoints Overview

(Refer to `http://localhost:8000/api/v1/docs` for detailed interactive documentation)

### Authentication & Users

-   **`POST /api/v1/users/`**: Create a new user.
    -   Request Body: `{"username": "string", "email": "user@example.com", "password": "string", "full_name": "optional_string"}`
-   **`POST /api/v1/auth/login/token`**: Login to get an access token.
    -   Request Body (form data): `username=string&password=string`
-   **`GET /api/v1/users/me`**: Get current authenticated user's details. (Requires JWT)

### Book Management

-   **`POST /api/v1/books/`**: Add a new book. (Requires JWT)
    -   Request Body: `{"title": "string", "author": "string", "isbn": "string", "total_quantity": integer}`
-   **`GET /api/v1/books/`**: List all books.
    -   Query Parameters: `skip` (int, default 0), `limit` (int, default 10), `title` (str), `author` (str)
-   **`GET /api/v1/books/{book_id}`**: Get a specific book.
-   **`DELETE /api/v1/books/{book_id}`**: Remove a book. (Requires JWT)

### Transactions

-   **`POST /api/v1/transactions/give`**: Lend a book. (Requires JWT)
    -   Request Body: `{"book_id": integer}`
-   **`POST /api/v1/transactions/take`**: Return a book. (Requires JWT)
    -   Request Body: `{"book_id": integer}`
-   **`GET /api/v1/transactions/`**: List all transactions.
    -   Query Parameters: `skip` (int, default 0), `limit` (int, default 10), `user_id` (int), `book_id` (int)

## Example API Requests (using cURL)

Replace `YOUR_ACCESS_TOKEN` with the token obtained from login.

1.  **Create a User:**

    ```bash
    curl -X POST "http://localhost:8000/api/v1/users/" \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "email": "test@example.com", "password": "password123", "full_name": "Test User"}'
    ```

2.  **Login:**

    ```bash
    curl -X POST "http://localhost:8000/api/v1/auth/login/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=testuser&password=password123"
    ```

    (Save the `access_token` from the response)

3.  **Add a New Book (Protected):**

    ```bash
    curl -X POST "http://localhost:8000/api/v1/books/" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "9780743273565", "total_quantity": 5}'
    ```

4.  **List Books (Public):**

    ```bash
    curl -X GET "http://localhost:8000/api/v1/books/?limit=2&title=Gatsby"
    ```

5.  **Lend a Book (Protected - assuming book ID 1 exists):**

    ```bash
    curl -X POST "http://localhost:8000/api/v1/transactions/give" \
    -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"book_id": 1}'
    ```

6.  **List Transactions (Public):**
    ```bash
    curl -X GET "http://localhost:8000/api/v1/transactions/"
    ```

## How to Run Tests

Tests are written using Pytest and run against an in-memory SQLite database.

1.  **Ensure dependencies are installed (including test dependencies):**
    If you only installed runtime dependencies via `pip install -r requirements.txt`, make sure `pytest` and `httpx` are also available. Usually, `requirements.txt` includes them.

2.  **Run tests from the project root directory:**

    **Method 1: Inside the Docker container (recommended for consistency):**

    ```bash
    docker-compose exec api pytest tests/
    ```

    **Method 2: Locally (requires local Python environment):**

    ```bash
    pytest tests/
    ```

    You should see output indicating the number of tests passed.
