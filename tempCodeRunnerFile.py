from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from typing import Optional
from passlib.hash import bcrypt
import jwt
import datetime

DATABASE_URL = "postgresql://movies_review:moviespass@localhost:5432/movie_review_db"  

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

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

Base.metadata.create_all(bind=engine)

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def encode(identity: int):
    payload = {
        "sub": identity,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
    return token

@app.post("/register")
async def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=user.email).first():
        return JSONResponse(status_code=400, content={"error": "Email already registered"})
    hashed_pw = bcrypt.hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(status_code=201, content={"message": "User registered successfully"})

@app.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(email=user.email).first()
    if db_user and bcrypt.verify(user.password, db_user.password):
        access_token = encode(identity=db_user.id)
        return JSONResponse(status_code=200, content={"access_token": access_token})
    return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

