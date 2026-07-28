# FastAPI Book API

A RESTful Book Management API built with **FastAPI**, **SQLAlchemy**, and **SQLite**. The project includes JWT authentication, role-based authorization, database migrations with Alembic, logging, and a clean modular architecture.

## Features

- User registration and login
- JWT authentication
- Role-based authorization (User / Admin)
- CRUD operations for books
- CRUD operations for categories
- Book filtering and searching
- Pagination and sorting
- SQLAlchemy ORM
- Alembic database migrations
- Custom exception handlers
- Application logging
- Modular project structure

## Technologies

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Alembic
- Pydantic
- JWT Authentication
- Passlib / Pwdlib
- Uvicorn

## Project Structure

```text
fastapi-book-api/
│
├── routers/
│   ├── authentication.py
│   ├── books.py
│   ├── categories.py
│   └── users.py
│
├── schemas/
│   ├── books.py
│   ├── categories.py
│   └── users.py
│
├── dependencies/
│   ├── auth.py
│   └── db.py
│
├── database.py
├── models.py
├── security.py
├── logger.py
├── exception_handlers.py
├── create_admin.py
├── main.py
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/AngelosGkiose/fastapi-book-api.git
```

Move into the project directory:

```bash
cd fastapi-book-api
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows**

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn main:app --reload
```

##  API Documentation

Once the server is running, open:

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

##  Authentication

The API uses JWT Bearer Tokens.

Available authentication endpoints:

- Register a new user
- Login
- Create admin user
- Protected endpoints
- Role-based access control

##  Books

Books support:

- Create
- Read
- Update
- Delete
- Search
- Filtering
- Sorting
- Pagination

##  Categories

Categories support:

- Create
- Read
- Update
- Delete

##  User Roles

### User

- View books
- View categories

### Admin

- Manage books
- Manage categories
- Access protected admin endpoints

## Logging

The application logs important events such as:

- Successful requests
- Errors
- Exceptions

## Future Improvements

- Reviews & Ratings
- Favorites
- File uploads
- Docker support
- Automated testing
- PostgreSQL support

## Author

Aggelos Gkiose
