from sqlalchemy.orm import Session
from sqlalchemy import and_
import models, schemas
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_user(db: Session, user: schemas.UserCreate, role: str = "user"):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(phone=user.phone, hashed_password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_books(db: Session, skip: int = 0, limit: int = 100):
    # Only return active books
    return db.query(models.Book).filter(models.Book.is_active == True).offset(skip).limit(limit).all()

def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.dict(), available_copies=book.total_copies, is_active=True)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: int, book: schemas.BookUpdate):
    db_book = get_book(db, book_id)
    if db_book:
        for key, value in book.dict().items():
            setattr(db_book, key, value)
        db.commit()
        db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if db_book:
        # Soft delete
        db_book.is_active = False
        db.commit()
        db.refresh(db_book)
    return db_book

def borrow_book(db: Session, user_id: int, book_id: int):
    book = get_book(db, book_id)
    if not book or book.available_copies < 1:
        return None
    
    # Check if user already borrowed this book and not returned
    active_borrow = db.query(models.Borrow).filter(
        and_(models.Borrow.user_id == user_id, models.Borrow.book_id == book_id, models.Borrow.is_returned == False)
    ).first()
    if active_borrow:
        return None

    borrow = models.Borrow(user_id=user_id, book_id=book_id)
    book.available_copies -= 1
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow

def return_book(db: Session, borrow_id: int):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id).first()
    if not borrow or borrow.is_returned:
        return None
    
    borrow.is_returned = True
    borrow.return_date = datetime.datetime.utcnow()
    
    book = get_book(db, borrow.book_id)
    book.available_copies += 1
    
    db.commit()
    db.refresh(borrow)
    return borrow

def get_user_borrows(db: Session, user_id: int):
    return db.query(models.Borrow).filter(models.Borrow.user_id == user_id).all()
