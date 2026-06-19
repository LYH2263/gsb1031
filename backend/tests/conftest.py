import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import database
import models
import crud
import schemas


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    from fastapi.testclient import TestClient
    import main

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    main.app.dependency_overrides[main.get_db] = _override_get_db
    c = TestClient(main.app)
    try:
        yield c
    finally:
        main.app.dependency_overrides.clear()


@pytest.fixture()
def normal_user(db_session):
    user = crud.create_user(
        db_session,
        schemas.UserCreate(phone="13800000000", password="password"),
        role="user",
    )
    return user


@pytest.fixture()
def sample_book(db_session):
    return crud.create_book(
        db_session,
        schemas.BookCreate(
            title="Test Book",
            author="Test Author",
            isbn="978-0-00-000000-1",
            total_copies=1,
        ),
    )


@pytest.fixture()
def out_of_stock_book(db_session):
    book = crud.create_book(
        db_session,
        schemas.BookCreate(
            title="Out Of Stock",
            author="Nobody",
            isbn="978-0-00-000000-2",
            total_copies=1,
        ),
    )
    book.available_copies = 0
    db_session.commit()
    db_session.refresh(book)
    return book
