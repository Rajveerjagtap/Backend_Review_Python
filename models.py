from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, validator
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
    year = Column(String)
    imdb_id = Column(String, unique=True, nullable=False)
    type = Column(String)
    poster = Column(String)
    imdb_rating = Column(String)
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

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class WriteReview(BaseModel):
    review_text: str
    rating: int

    @validator('rating')
    def rating_range(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

    @validator('review_text')
    def review_length(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Review text cannot be empty')
        if len(v) > 300:
            raise ValueError('Review text must be 300 characters or less')
        return v


class UpdateReview(BaseModel):
    review_text: Optional[str] = None
    rating: Optional[int] = None

    @validator('rating')
    def rating_range(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

    @validator('review_text')
    def review_length(cls, v):
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('Review text cannot be empty')
            if len(v) > 300:
                raise ValueError('Review text must be 300 characters or less')
        return v

    class Config:
        from_attributes = True
