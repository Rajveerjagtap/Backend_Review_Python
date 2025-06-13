from turtle import title
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from passlib.hash import bcrypt
import jwt
import datetime
from models import User, UserLogin, UserRegister
from utils import encode, get_db
from database import SessionLocal, engine, Base
from routes.auth import register_user, login_user
from routes.omdb import *

app = FastAPI()

register_user(app)
login_user(app)

@app.get("/")
async def root():
    return {"message": "Movie Review API is running!"}


@app.get("/search")
def search():
    search()