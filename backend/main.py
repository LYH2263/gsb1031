from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import models, schemas, crud, database
from jose import JWTError, jwt
import datetime
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import os
import shutil

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Mount static files
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Startup logic merged into the main startup_event below

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

import random
from pydantic import BaseModel

# Auth config
SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# In-memory store for SMS codes (for demonstration purposes)
sms_codes = {}

class SMSRequest(BaseModel):
    phone: str

@app.post("/send-sms")
def send_sms(request: SMSRequest):
    code = str(random.randint(100000, 999999))
    sms_codes[request.phone] = code
    # In a real app, you would send the SMS here.
    # For simulation, we return the code to the frontend.
    return {"code": code}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone: str = payload.get("sub")
        if phone is None:
            raise credentials_exception
        token_data = schemas.TokenData(phone=phone)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_phone(db, phone=token_data.phone)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_admin_user)):
    try:
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        # Return the full URL. In production, this should be configured properly.
        # For this setup, we assume localhost:8000
        return {"url": f"http://localhost:8000/uploads/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_phone(db, phone=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.phone}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    # Verify SMS code
    if user.phone not in sms_codes or sms_codes[user.phone] != user.verification_code:
        raise HTTPException(status_code=400, detail="验证码错误或已过期")
    
    # Clean up used code
    del sms_codes[user.phone]

    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="该手机号已注册")
    # Convert UserRegister to UserCreate for CRUD
    user_create = schemas.UserCreate(phone=user.phone, password=user.password)
    return crud.create_user(db=db, user=user_create)

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/books/", response_model=List[schemas.BookWithUserStatus])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    books = crud.get_books(db, skip=skip, limit=limit)
    
    # Get user's borrow history
    borrows = crud.get_user_borrows(db, user_id=current_user.id)
    borrowing_ids = {b.book_id for b in borrows if not b.is_returned}
    borrowed_history_ids = {b.book_id for b in borrows}
    
    for book in books:
        book.is_borrowing = book.id in borrowing_ids
        book.has_borrowed = book.id in borrowed_history_ids
        
    return books

@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.create_book(db=db, book=book)

@app.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.update_book(db=db, book_id=book_id, book=book)

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    crud.delete_book(db=db, book_id=book_id)
    return {"ok": True}

@app.post("/borrows/", response_model=schemas.Borrow)
def borrow_book(borrow: schemas.BorrowCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_borrow = crud.borrow_book(db=db, user_id=current_user.id, book_id=borrow.book_id)
    if db_borrow is None:
        raise HTTPException(status_code=400, detail="图书库存不足或您已借阅该书且未归还")
    return db_borrow

@app.post("/borrows/{borrow_id}/return", response_model=schemas.Borrow)
def return_book(borrow_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    borrow = db.query(models.Borrow).filter(models.Borrow.id == borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=404, detail="未找到借阅记录")
    if borrow.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
        
    db_borrow = crud.return_book(db=db, borrow_id=borrow_id)
    if db_borrow is None:
        raise HTTPException(status_code=400, detail="无法归还图书")
    return db_borrow

@app.get("/my-borrows", response_model=List[schemas.Borrow])
def read_my_borrows(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_user_borrows(db, user_id=current_user.id)

@app.on_event("startup")
def startup_event():
    # Ensure all assets are copied to uploads
    if os.path.exists("assets"):
        for filename in os.listdir("assets"):
            src = os.path.join("assets", filename)
            dst = os.path.join("uploads", filename)
            if os.path.isfile(src) and not os.path.exists(dst):
                try:
                    shutil.copy(src, dst)
                    print(f"Copied {filename} to uploads")
                except Exception as e:
                    print(f"Failed to copy {filename}: {e}")

    with database.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE books ADD COLUMN cover_url VARCHAR"))
            print("Migration: Added cover_url column to books table")
        except Exception as e:
            pass

    db = database.SessionLocal()
    
    # Initialize default users if they don't exist
    # Normal user
    user = crud.get_user_by_phone(db, "13800000000")
    if not user:
        crud.create_user(db, schemas.UserCreate(phone="13800000000", password="password"), role="user")
        print("Default user created.")
        
    # Admin user
    admin = crud.get_user_by_phone(db, "13900000000")
    if not admin:
        crud.create_user(db, schemas.UserCreate(phone="13900000000", password="password"), role="admin")
        print("Default admin created.")

    # Check if books exist or are incomplete
    books_count = db.query(models.Book).count()
    # If we have very few books (e.g., only 1 from a failed init), try to load seed data again
    if books_count < 10:
        print(f"Books count is {books_count}, attempting to load/reload seed data...")
        try:
            with open("seed.sql", "r", encoding="utf-8") as f:
                sql_script = f.read()
                statements = [s.strip() for s in sql_script.split(';') if s.strip()]
                for statement in statements:
                    try:
                        db.execute(text(statement))
                        db.commit()
                    except Exception as e:
                        # Likely integrity error (duplicate), rollback and continue
                        db.rollback()
                print("Seed data loading attempt finished.")
        except Exception as e:
            print(f"Error loading seed data: {e}")
            
    db.close()
