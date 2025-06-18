from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from models import User, UserLogin, UserRegister
from utils import encode, get_db

def register_user(app):
    @app.post("/register")
    async def register(user: UserRegister, db: Session = Depends(get_db)):
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        
        hashed_pw = bcrypt.hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_pw
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return JSONResponse(
            status_code=201, 
            content={
                "message": "User registered successfully",
                "user_id": new_user.id,
                "username": new_user.username
            }
        )

def login_user(app):
    @app.post("/login")
    async def login(user: UserLogin, db: Session = Depends(get_db)):
        db_user = db.query(User).filter(User.email == user.email).first()
        
        if not db_user or not bcrypt.verify(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        access_token = encode(identity=db_user.id)
        
        return JSONResponse(
            status_code=200, 
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": db_user.id,
                "username": db_user.username,
                "expires_in": 86400 
            }
        )