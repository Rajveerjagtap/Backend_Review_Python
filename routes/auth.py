from fastapi import Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from models import User, UserLogin, UserRegister
from utils import encode, get_db


def register_user(app):
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

def login_user(app):
    @app.post("/login")
    async def login(user: UserLogin, db: Session = Depends(get_db)):
        db_user = db.query(User).filter_by(email=user.email).first()
        if db_user and bcrypt.verify(user.password, db_user.password):
            access_token = encode(identity=db_user.id)
            return JSONResponse(status_code=200, content={"access_token": access_token})
        return JSONResponse(status_code=401, content={"error": "Invalid credentials"})