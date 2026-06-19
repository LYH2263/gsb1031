import crud


class TestBorrowBook:
    def test_borrow_success_decrements_available_copies(self, db_session, normal_user, sample_book):
        assert sample_book.available_copies == 1

        borrow = crud.borrow_book(db_session, user_id=normal_user.id, book_id=sample_book.id)

        assert borrow is not None
        assert borrow.user_id == normal_user.id
        assert borrow.book_id == sample_book.id
        assert borrow.is_returned is False
        assert borrow.return_date is None

        db_session.refresh(sample_book)
        assert sample_book.available_copies == 0

    def test_borrow_fails_when_out_of_stock(self, db_session, normal_user, out_of_stock_book):
        assert out_of_stock_book.available_copies == 0

        borrow = crud.borrow_book(
            db_session, user_id=normal_user.id, book_id=out_of_stock_book.id
        )

        assert borrow is None

    def test_borrow_fails_when_user_already_borrowed_and_not_returned(
        self, db_session, normal_user, sample_book
    ):
        first = crud.borrow_book(db_session, user_id=normal_user.id, book_id=sample_book.id)
        assert first is not None

        sample_book.available_copies = 5
        db_session.commit()
        db_session.refresh(sample_book)

        second = crud.borrow_book(db_session, user_id=normal_user.id, book_id=sample_book.id)

        assert second is None
        db_session.refresh(sample_book)
        assert sample_book.available_copies == 5


class TestReturnBook:
    def test_return_success_increments_available_copies(
        self, db_session, normal_user, sample_book
    ):
        borrow = crud.borrow_book(db_session, user_id=normal_user.id, book_id=sample_book.id)
        assert borrow is not None
        db_session.refresh(sample_book)
        assert sample_book.available_copies == 0

        returned = crud.return_book(db_session, borrow_id=borrow.id)

        assert returned is not None
        assert returned.is_returned is True
        assert returned.return_date is not None

        db_session.refresh(sample_book)
        assert sample_book.available_copies == 1

    def test_return_fails_when_already_returned(self, db_session, normal_user, sample_book):
        borrow = crud.borrow_book(db_session, user_id=normal_user.id, book_id=sample_book.id)
        crud.return_book(db_session, borrow_id=borrow.id)

        again = crud.return_book(db_session, borrow_id=borrow.id)

        assert again is None

    def test_return_then_borrow_again_succeeds(self, db_session, normal_user, sample_book):
        borrow1 = crud.borrow_book(db_session, user_id=normal_user.id, book_id=sample_book.id)
        crud.return_book(db_session, borrow_id=borrow1.id)

        borrow2 = crud.borrow_book(db_session, user_id=normal_user.id, book_id=sample_book.id)

        assert borrow2 is not None
        assert borrow2.id != borrow1.id
        db_session.refresh(sample_book)
        assert sample_book.available_copies == 0
