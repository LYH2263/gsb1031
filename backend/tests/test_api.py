import pytest
import crud
import models
import schemas


def test_full_borrow_flow(client, db_session):
    user = crud.create_user(
        db_session,
        schemas.UserCreate(phone="13800000000", password="password"),
        role="user"
    )
    
    book = models.Book(
        title="三体",
        author="刘慈欣",
        isbn="9787536692930",
        total_copies=5,
        available_copies=5,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    
    login_response = client.post(
        "/token",
        data={"username": "13800000000", "password": "password"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    borrow_response = client.post(
        "/borrows/",
        json={"book_id": book.id},
        headers=headers
    )
    assert borrow_response.status_code == 200
    borrow_data = borrow_response.json()
    assert borrow_data["user_id"] == user.id
    assert borrow_data["book_id"] == book.id
    assert borrow_data["is_returned"] is False
    borrow_id = borrow_data["id"]
    
    my_borrows_response = client.get("/my-borrows", headers=headers)
    assert my_borrows_response.status_code == 200
    my_borrows = my_borrows_response.json()
    assert len(my_borrows) == 1
    assert my_borrows[0]["id"] == borrow_id
    assert my_borrows[0]["is_returned"] is False
    
    return_response = client.post(
        f"/borrows/{borrow_id}/return",
        headers=headers
    )
    assert return_response.status_code == 200
    return_data = return_response.json()
    assert return_data["id"] == borrow_id
    assert return_data["is_returned"] is True
    assert return_data["return_date"] is not None
    
    db_session.refresh(book)
    assert book.available_copies == 5


def test_borrow_out_of_stock_api(client, db_session):
    user = crud.create_user(
        db_session,
        schemas.UserCreate(phone="13800000001", password="password"),
        role="user"
    )
    
    book = models.Book(
        title="Test Book",
        author="Test Author",
        isbn="1111111111",
        total_copies=1,
        available_copies=0,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    
    login_response = client.post(
        "/token",
        data={"username": "13800000001", "password": "password"}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.post(
        "/borrows/",
        json={"book_id": book.id},
        headers=headers
    )
    assert response.status_code == 400


def test_duplicate_borrow_api(client, db_session):
    user = crud.create_user(
        db_session,
        schemas.UserCreate(phone="13800000002", password="password"),
        role="user"
    )
    
    book = models.Book(
        title="Test Book 2",
        author="Test Author",
        isbn="2222222222",
        total_copies=3,
        available_copies=3,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    
    login_response = client.post(
        "/token",
        data={"username": "13800000002", "password": "password"}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    first_response = client.post(
        "/borrows/",
        json={"book_id": book.id},
        headers=headers
    )
    assert first_response.status_code == 200
    
    second_response = client.post(
        "/borrows/",
        json={"book_id": book.id},
        headers=headers
    )
    assert second_response.status_code == 400
