import pytest
import crud
import models
import schemas


def test_borrow_book_out_of_stock(db_session):
    user = crud.create_user(
        db_session, 
        schemas.UserCreate(phone="13800000001", password="testpass"),
        role="user"
    )
    
    book = models.Book(
        title="Test Book",
        author="Test Author",
        isbn="1234567890",
        total_copies=1,
        available_copies=0,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    
    result = crud.borrow_book(db_session, user_id=user.id, book_id=book.id)
    
    assert result is None


def test_borrow_book_duplicate_borrow(db_session):
    user = crud.create_user(
        db_session, 
        schemas.UserCreate(phone="13800000002", password="testpass"),
        role="user"
    )
    
    book = models.Book(
        title="Test Book 2",
        author="Test Author",
        isbn="1234567891",
        total_copies=2,
        available_copies=2,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    
    first_borrow = crud.borrow_book(db_session, user_id=user.id, book_id=book.id)
    assert first_borrow is not None
    assert first_borrow.is_returned is False
    
    db_session.refresh(book)
    assert book.available_copies == 1
    
    second_borrow = crud.borrow_book(db_session, user_id=user.id, book_id=book.id)
    
    assert second_borrow is None


def test_borrow_and_return_normal(db_session):
    user = crud.create_user(
        db_session, 
        schemas.UserCreate(phone="13800000003", password="testpass"),
        role="user"
    )
    
    book = models.Book(
        title="Test Book 3",
        author="Test Author",
        isbn="1234567892",
        total_copies=1,
        available_copies=1,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    
    borrow = crud.borrow_book(db_session, user_id=user.id, book_id=book.id)
    
    assert borrow is not None
    assert borrow.user_id == user.id
    assert borrow.book_id == book.id
    assert borrow.is_returned is False
    assert borrow.return_date is None
    
    db_session.refresh(book)
    assert book.available_copies == 0
    
    returned = crud.return_book(db_session, borrow_id=borrow.id)
    
    assert returned is not None
    assert returned.is_returned is True
    assert returned.return_date is not None
    
    db_session.refresh(book)
    assert book.available_copies == 1


def test_return_already_returned_book(db_session):
    user = crud.create_user(
        db_session, 
        schemas.UserCreate(phone="13800000004", password="testpass"),
        role="user"
    )
    
    book = models.Book(
        title="Test Book 4",
        author="Test Author",
        isbn="1234567893",
        total_copies=1,
        available_copies=1,
        is_active=True
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    
    borrow = crud.borrow_book(db_session, user_id=user.id, book_id=book.id)
    crud.return_book(db_session, borrow_id=borrow.id)
    
    second_return = crud.return_book(db_session, borrow_id=borrow.id)
    
    assert second_return is None
