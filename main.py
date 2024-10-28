from typing import List, Union
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, Relationship, select
from typing_extensions import Annotated, Optional
from datetime import datetime

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class User(SQLModel, table=True):
    __tablename__= "users"

    id: int = Field(default=None, primary_key=True)
    email: str = Field(default=None)
    first_name: str = Field(default=None)
    last_name: str = Field (default=None)

    books_owned: List["Book"] = Relationship(back_populates="owner")
    books_reviewed: List["Book_Review"] = Relationship(back_populates="book_reviewer")

    reviews_by_user: List["User_Review"] = Relationship(back_populates="user_reviews")
    reviews_of_user: List["User_Review"] = Relationship(back_populates="reviewee")

    borrow_history: List["Borrow"] = Relationship(back_populates="borrower")


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: int = Field(primary_key=True)
    title: str = Field(default=None)
    author: str = Field(default=None)
    isbn: str = Field(default=None)
    image_link: str = Field(default=None)
    genre: str = Field(default=None)
    pages: int = Field(default=0)

    owner_id: int = Field(foreign_key="users.id")
    owner: "User" = Relationship(back_populates="books_owned")

    reviews: List["Book_Review"] = Relationship(back_populates="book")
    borrows: List["Borrow"] = Relationship(back_populates="book")

class Book_Review(SQLModel, table=True):
    __tablename__ = "book_reviews"

    id: int = Field(primary_key=True)
    rating: int = Field(default=None)
    body: str = Field(default=None)

    book_id: int = Field(foreign_key="books.id")
    book: "Book" = Relationship(back_populates="reviews")

    reviewer_id: int = Field(foreign_key="users.id")
    reviewer: "User" = Relationship(back_populates="books_reviewed")

class User_Review(SQLModel, table=True):
    __tablename__ = "user_reviews"

    id: int = Field(primary_key=True)
    rating: int = Field(default=None)
    body: str = Field(default=None)

    reviewer_id: int = Field(foreign_key="users.id")
    user_reviews: "User" = Relationship(back_populates="reviews_by_user")

    reviewee_id: int = Field(foreign_key="users.id")
    reviewee: "User" = Relationship(back_populates="reviews_of_user")

class Borrow(SQLModel, table=True):
    __tablename__="borrows"

    id: int = Field(primary_key=True)
    date_borrowed: datetime = Field(default=datetime.now())

    book_id: int = Field(foreign_key="books.id")
    book: "Book" = Relationship(back_populates="borrows")

    borrower_id: int = Field(foreign_key="users.id")
    borrower: "User" = Relationship(back_populates="borrow_history")


@app.get("/")
async def root():
    return {"message": "Book Borrower Root"}