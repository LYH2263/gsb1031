import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="function")
def db_session():
    import models
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        models.Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    from main import app, sms_codes, get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    original_on_startup = app.router.on_startup[:]
    app.router.on_startup.clear()

    original_on_shutdown = app.router.on_shutdown[:]
    app.router.on_shutdown.clear()

    sms_codes.clear()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    app.router.on_startup = original_on_startup
    app.router.on_shutdown = original_on_shutdown
    sms_codes.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    import crud
    import schemas
    user = crud.create_user(
        db_session,
        schemas.UserCreate(phone="13800000001", password="testpass123"),
        role="user"
    )
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_book(db_session):
    import models
    book = models.Book(
        title="测试图书",
        author="测试作者",
        isbn="978-0000000001",
        total_copies=2,
        available_copies=2,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book
