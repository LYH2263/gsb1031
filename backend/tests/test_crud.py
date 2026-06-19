import pytest
import models
import crud
import schemas


def test_borrow_book_insufficient_stock(db_session, test_user, test_book):
    test_book.available_copies = 0
    db_session.commit()

    result = crud.borrow_book(db_session, user_id=test_user.id, book_id=test_book.id)
    assert result is None
    db_session.refresh(test_book)
    assert test_book.available_copies == 0


def test_borrow_book_insufficient_stock_book_not_found(db_session, test_user):
    result = crud.borrow_book(db_session, user_id=test_user.id, book_id=9999)
    assert result is None


def test_borrow_book_already_borrowed_not_returned(db_session, test_user, test_book):
    first_borrow = crud.borrow_book(db_session, user_id=test_user.id, book_id=test_book.id)
    assert first_borrow is not None
    assert test_book.available_copies == 1

    second_borrow = crud.borrow_book(db_session, user_id=test_user.id, book_id=test_book.id)
    assert second_borrow is None
    db_session.refresh(test_book)
    assert test_book.available_copies == 1


def test_borrow_and_return_normal_flow(db_session, test_user, test_book):
    assert test_book.available_copies == 2

    borrow = crud.borrow_book(db_session, user_id=test_user.id, book_id=test_book.id)
    assert borrow is not None
    assert borrow.user_id == test_user.id
    assert borrow.book_id == test_book.id
    assert borrow.is_returned is False
    assert borrow.borrow_date is not None
    assert borrow.return_date is None
    db_session.refresh(test_book)
    assert test_book.available_copies == 1

    borrow2 = crud.borrow_book(db_session, user_id=test_user.id + 1, book_id=test_book.id)
    assert borrow2 is not None
    db_session.refresh(test_book)
    assert test_book.available_copies == 0

    result = crud.borrow_book(db_session, user_id=test_user.id + 2, book_id=test_book.id)
    assert result is None

    returned = crud.return_book(db_session, borrow_id=borrow.id)
    assert returned is not None
    assert returned.is_returned is True
    assert returned.return_date is not None
    db_session.refresh(test_book)
    assert test_book.available_copies == 1

    returned_again = crud.return_book(db_session, borrow_id=borrow.id)
    assert returned_again is None
    db_session.refresh(test_book)
    assert test_book.available_copies == 1


def test_return_book_not_found(db_session):
    result = crud.return_book(db_session, borrow_id=9999)
    assert result is None
