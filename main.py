from typing import List
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
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

    books_owned: Optional[List["Book"]] = Relationship(back_populates="owner")
    books_reviewed: Optional[List["Book_Review"]] = Relationship(back_populates="book_reviewer")

    reviews_by_user: Optional[List["User_Review"]] = Relationship(
        back_populates="user_reviews",
        sa_relationship_kwargs={'foreign_keys': 'User_Review.reviewer_id'}
        )
    reviews_of_user: Optional[List["User_Review"]] = Relationship(
        back_populates="reviewee",
        sa_relationship_kwargs={'foreign_keys': 'User_Review.reviewer_id'}
        )

    borrow_history: Optional[List["Borrow"]] = Relationship(back_populates="borrower")


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
    book_reviewer: "User" = Relationship(back_populates="books_reviewed")

class User_Review(SQLModel, table=True):
    __tablename__ = "user_reviews"

    id: int = Field(primary_key=True)
    rating: int = Field(default=None)
    body: str = Field(default=None)

    reviewer_id: int = Field(foreign_key="users.id")
    user_reviews: "User" = Relationship(
        back_populates="reviews_by_user",
        sa_relationship_kwargs={'foreign_keys': '[User_Review.reviewer_id]'}
        )

    reviewee_id: int = Field(foreign_key="users.id")
    reviewee: "User" = Relationship(
        back_populates="reviews_of_user",
        sa_relationship_kwargs={'foreign_keys': '[User_Review.reviewee_id]'}
        )

class Borrow(SQLModel, table=True):
    __tablename__="borrows"

    id: int = Field(primary_key=True)
    date_borrowed: datetime = Field(default=datetime.now())

    book_id: int = Field(foreign_key="books.id")
    book: "Book" = Relationship(back_populates="borrows")

    borrower_id: int = Field(foreign_key="users.id")
    borrower: "User" = Relationship(back_populates="borrow_history")


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