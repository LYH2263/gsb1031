import pytest
import crud
import schemas


class TestBorrowBook:
    def test_borrow_book_normal(self, db, test_user, test_book):
        borrow = crud.borrow_book(db, user_id=test_user.id, book_id=test_book.id)

        assert borrow is not None
        assert borrow.user_id == test_user.id
        assert borrow.book_id == test_book.id
        assert borrow.is_returned is False
        assert borrow.return_date is None

        db.refresh(test_book)
        assert test_book.available_copies == 0

    def test_borrow_book_insufficient_stock(self, db, test_user, test_book):
        crud.borrow_book(db, user_id=test_user.id, book_id=test_book.id)
        db.refresh(test_book)
        assert test_book.available_copies == 0

        borrow = crud.borrow_book(db, user_id=test_user.id, book_id=test_book.id)
        assert borrow is None

        another_user = crud.create_user(
            db,
            schemas.UserCreate(phone="138******01", password="password"),
            role="user"
        )
        borrow_another = crud.borrow_book(db, user_id=another_user.id, book_id=test_book.id)
        assert borrow_another is None

    def test_borrow_book_duplicate_not_returned(self, db, test_user, test_book_with_copies):
        first_borrow = crud.borrow_book(db, user_id=test_user.id, book_id=test_book_with_copies.id)
        assert first_borrow is not None

        db.refresh(test_book_with_copies)
        assert test_book_with_copies.available_copies == 2

        second_borrow = crud.borrow_book(db, user_id=test_user.id, book_id=test_book_with_copies.id)
        assert second_borrow is None

        db.refresh(test_book_with_copies)
        assert test_book_with_copies.available_copies == 2


class TestReturnBook:
    def test_return_book_normal(self, db, test_user, test_book):
        borrow = crud.borrow_book(db, user_id=test_user.id, book_id=test_book.id)
        assert borrow is not None
        db.refresh(test_book)
        assert test_book.available_copies == 0

        returned = crud.return_book(db, borrow_id=borrow.id)
        assert returned is not None
        assert returned.is_returned is True
        assert returned.return_date is not None

        db.refresh(test_book)
        assert test_book.available_copies == 1

    def test_return_already_returned(self, db, test_user, test_book):
        borrow = crud.borrow_book(db, user_id=test_user.id, book_id=test_book.id)
        crud.return_book(db, borrow_id=borrow.id)

        returned_again = crud.return_book(db, borrow_id=borrow.id)
        assert returned_again is None

    def test_return_nonexistent_borrow(self, db):
        result = crud.return_book(db, borrow_id=9999)
        assert result is None


class TestBorrowReturnFlow:
    def test_borrow_then_return_then_borrow_again(self, db, test_user, test_book):
        borrow1 = crud.borrow_book(db, user_id=test_user.id, book_id=test_book.id)
        assert borrow1 is not None
        db.refresh(test_book)
        assert test_book.available_copies == 0

        crud.return_book(db, borrow_id=borrow1.id)
        db.refresh(test_book)
        assert test_book.available_copies == 1

        borrow2 = crud.borrow_book(db, user_id=test_user.id, book_id=test_book.id)
        assert borrow2 is not None
        assert borrow2.id != borrow1.id
        db.refresh(test_book)
        assert test_book.available_copies == 0
