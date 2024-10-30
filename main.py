from typing import List
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from typing_extensions import Annotated
from models import User, Book, Book_Review, User_Review, Borrow
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

rds_postgres_url = os.getenv("AWS_POSTGRES_RDS_URL")

# for SQLite connection and testing
# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
# connect_args = {"check_same_thread": False}
# engine = create_engine(rds_postgres_url, connect_args=connect_args, echo=True)

engine = create_engine(rds_postgres_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

@app.post("/api/users")
def add_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/api/users")
def get_users(session: SessionDep) -> List[User]:
    all_users = session.exec(select(User)).all()
    return all_users

@app.get("/api/users/{user_id}")
def get_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/books")
def add_book(book: Book, session: SessionDep) -> Book:
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@app.get("/api/books/{book_id}")
def get_book(book_id: int, session: SessionDep) -> Book:
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/api/book-reviews/")
def add_review(book_review: Book_Review, session: SessionDep) -> Book_Review:
    session.add(book_review)
    session.commit()
    session.refresh(book_review)
    return book_review


@app.post("/api/user-reviews/")
def add_user_review(user_review: User_Review, session: SessionDep) -> User_Review:
    session.add(user_review)
    session.commit()
    session.refresh(user_review)
    return user_review

@app.post("/api/borrows/")
def add_borrow(borrow: Borrow, session: SessionDep) -> Borrow:
    session.add(borrow)
    session.commit()
    session.refresh(borrow)
    return borrow

@app.get("/")
async def root():
    return {"message": "Book Borrower Root"}