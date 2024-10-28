from sqlmodel import Field, SQLModel, Relationship
from typing_extensions import Optional
from typing import List
from datetime import datetime

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