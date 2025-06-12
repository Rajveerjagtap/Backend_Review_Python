from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    reviews = relationship("Reviews", back_populates="user")

class Movies(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    release_date = Column(String)
    director = Column(String)
    reviews = relationship("Reviews", back_populates="movie")

class Reviews(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey('movies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    review_text = Column(String)
    rating = Column(Integer)
    movie = relationship("Movies", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Movie(BaseModel):
    title: str
    description: str
    release_date: str
    director: str

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[str] = None
    director: Optional[str] = None

class WriteReview(BaseModel):
    movie_id: int
    user_id: int
    review_text: str
    rating: int

class UpdateReview(BaseModel):
    id: int
    review_text: Optional[str] = None
    rating: Optional[int] = None

