import pytest
from fastapi.testclient import TestClient


def test_full_borrow_flow(client, db_session):
    import models

    book = models.Book(
        title="集成测试图书",
        author="测试作者",
        isbn="978-0000000099",
        total_copies=3,
        available_copies=3,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    phone = "13800000099"
    password = "testpass123"

    sms_resp = client.post("/send-sms", json={"phone": phone})
    assert sms_resp.status_code == 200
    code = sms_resp.json()["code"]

    register_resp = client.post(
        "/users/",
        json={"phone": phone, "password": password, "verification_code": code}
    )
    assert register_resp.status_code == 200
    user_data = register_resp.json()
    assert user_data["phone"] == phone
    assert user_data["role"] == "user"

    login_resp = client.post(
        "/token",
        data={"username": phone, "password": password}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_resp = client.get("/users/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["phone"] == phone

    borrow_resp = client.post(
        "/borrows/",
        json={"book_id": book.id},
        headers=headers
    )
    assert borrow_resp.status_code == 200
    borrow_data = borrow_resp.json()
    assert borrow_data["book_id"] == book.id
    assert borrow_data["is_returned"] is False
    borrow_id = borrow_data["id"]

    db_session.refresh(book)
    assert book.available_copies == 2

    my_borrows_resp = client.get("/my-borrows", headers=headers)
    assert my_borrows_resp.status_code == 200
    borrows = my_borrows_resp.json()
    assert len(borrows) >= 1
    found = any(b["id"] == borrow_id and not b["is_returned"] for b in borrows)
    assert found is True

    return_resp = client.post(f"/borrows/{borrow_id}/return", headers=headers)
    assert return_resp.status_code == 200
    return_data = return_resp.json()
    assert return_data["id"] == borrow_id
    assert return_data["is_returned"] is True
    assert return_data["return_date"] is not None

    db_session.refresh(book)
    assert book.available_copies == 3

    my_borrows_resp2 = client.get("/my-borrows", headers=headers)
    assert my_borrows_resp2.status_code == 200
    borrows2 = my_borrows_resp2.json()
    found_returned = any(b["id"] == borrow_id and b["is_returned"] for b in borrows2)
    assert found_returned is True


def test_borrow_book_without_auth(client):
    resp = client.post("/borrows/", json={"book_id": 1})
    assert resp.status_code == 401


def test_borrow_nonexistent_book(client, db_session):
    import crud
    import schemas

    user = crud.create_user(
        db_session,
        schemas.UserCreate(phone="13800000002", password="pass123"),
        role="user"
    )
    db_session.commit()

    login_resp = client.post(
        "/token",
        data={"username": "13800000002", "password": "pass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/borrows/", json={"book_id": 99999}, headers=headers)
    assert resp.status_code == 400


def test_duplicate_borrow_rejected(client, db_session):
    import models
    import crud
    import schemas

    book = models.Book(
        title="重复借阅测试",
        author="作者",
        isbn="978-0000000088",
        total_copies=2,
        available_copies=2,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    user = crud.create_user(
        db_session,
        schemas.UserCreate(phone="13800000003", password="pass123"),
        role="user"
    )
    db_session.commit()

    login_resp = client.post(
        "/token",
        data={"username": "13800000003", "password": "pass123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r1 = client.post("/borrows/", json={"book_id": book.id}, headers=headers)
    assert r1.status_code == 200

    r2 = client.post("/borrows/", json={"book_id": book.id}, headers=headers)
    assert r2.status_code == 400
