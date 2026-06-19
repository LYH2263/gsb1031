import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
import database
import models
import crud
import schemas


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

_test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

database.engine = _test_engine
database.SessionLocal = _TestingSessionLocal

from main import app, get_db


def override_get_db():
    try:
        db = _TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def fresh_db():
    models.Base.metadata.create_all(bind=_test_engine)
    yield
    models.Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def client():
    db = _TestingSessionLocal()

    crud.create_user(
        db,
        schemas.UserCreate(phone="138******00", password="password"),
        role="user"
    )

    crud.create_book(
        db,
        schemas.BookCreate(
            title="Integration Test Book",
            author="Test Author",
            isbn="1111111111",
            total_copies=2
        )
    )
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c


class TestBorrowFlowIntegration:
    def test_full_borrow_return_flow(self, client):
        login_response = client.post(
            "/token",
            data={"username": "138******00", "password": "password"}
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        books_response = client.get("/books/", headers=headers)
        assert books_response.status_code == 200
        books = books_response.json()
        assert len(books) >= 1
        book_id = books[0]["id"]
        assert books[0]["available_copies"] == 2

        borrow_response = client.post(
            "/borrows/",
            json={"book_id": book_id},
            headers=headers
        )
        assert borrow_response.status_code == 200
        borrow_data = borrow_response.json()
        assert borrow_data["book_id"] == book_id
        assert borrow_data["is_returned"] is False
        borrow_id = borrow_data["id"]

        my_borrows_response = client.get("/my-borrows", headers=headers)
        assert my_borrows_response.status_code == 200
        my_borrows = my_borrows_response.json()
        assert len(my_borrows) >= 1
        my_borrow = next(b for b in my_borrows if b["id"] == borrow_id)
        assert my_borrow["is_returned"] is False

        books_after_borrow = client.get("/books/", headers=headers)
        assert books_after_borrow.status_code == 200
        book_after = next(b for b in books_after_borrow.json() if b["id"] == book_id)
        assert book_after["available_copies"] == 1

        return_response = client.post(
            f"/borrows/{borrow_id}/return",
            headers=headers
        )
        assert return_response.status_code == 200
        return_data = return_response.json()
        assert return_data["id"] == borrow_id
        assert return_data["is_returned"] is True
        assert return_data["return_date"] is not None

        my_borrows_after_return = client.get("/my-borrows", headers=headers)
        assert my_borrows_after_return.status_code == 200
        borrows_after = my_borrows_after_return.json()
        borrow_after_return = next(b for b in borrows_after if b["id"] == borrow_id)
        assert borrow_after_return["is_returned"] is True

        books_after_return = client.get("/books/", headers=headers)
        assert books_after_return.status_code == 200
        book_final = next(b for b in books_after_return.json() if b["id"] == book_id)
        assert book_final["available_copies"] == 2

    def test_duplicate_borrow_should_fail(self, client):
        login_response = client.post(
            "/token",
            data={"username": "138******00", "password": "password"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        books = client.get("/books/", headers=headers).json()
        book_id = books[0]["id"]

        r1 = client.post("/borrows/", json={"book_id": book_id}, headers=headers)
        assert r1.status_code == 200

        r2 = client.post("/borrows/", json={"book_id": book_id}, headers=headers)
        assert r2.status_code == 400
        assert "库存不足或您已借阅" in r2.json()["detail"]
