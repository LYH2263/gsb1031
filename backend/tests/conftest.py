import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base
import models
import crud
import schemas


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(db):
    user = crud.create_user(
        db,
        schemas.UserCreate(phone="138******00", password="password"),
        role="user"
    )
    return user


@pytest.fixture(scope="function")
def test_book(db):
    book = crud.create_book(
        db,
        schemas.BookCreate(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            total_copies=1
        )
    )
    return book


@pytest.fixture(scope="function")
def test_book_with_copies(db):
    book = crud.create_book(
        db,
        schemas.BookCreate(
            title="Multi Copy Book",
            author="Test Author",
            isbn="0987654321",
            total_copies=3
        )
    )
    return book
