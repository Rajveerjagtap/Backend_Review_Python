import jwt
import datetime
from sqlalchemy.orm import Session
from database import SessionLocal


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