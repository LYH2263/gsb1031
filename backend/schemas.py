from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    cover_url: Optional[str] = None
    total_copies: int

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    available_copies: int

class Book(BookBase):
    id: int
    available_copies: int
    is_active: bool
    class Config:
        orm_mode = True

class BookWithUserStatus(Book):
    is_borrowing: bool = False
    has_borrowed: bool = False

class UserBase(BaseModel):
    phone: str

class UserCreate(UserBase):
    password: str

class UserRegister(UserCreate):
    verification_code: str

class User(UserBase):
    id: int
    is_active: bool
    role: str
    class Config:
        orm_mode = True

class BorrowBase(BaseModel):
    book_id: int

class BorrowCreate(BorrowBase):
    pass

class Borrow(BaseModel):
    id: int
    user_id: int
    book_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool
    book: Book
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone: Optional[str] = None
