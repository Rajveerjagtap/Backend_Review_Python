from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import User, UserLogin, UserRegister, Movies
from utils import encode, get_db
from database import engine, Base
from routes.auth import register_user, login_user
from routes.tmdb import search

app = FastAPI()

Base.metadata.create_all(bind=engine)

register_user(app)
login_user(app)

@app.get("/")
async def root():
    return {"message": "Movie Review API is running!"}


@app.get("/search/{title}")
async def search_movie(title: str, db: Session = Depends(get_db)):
    try:
        movie = search(title, db)
        if movie:
            return {
                "success": True,
                "movie": {
                    "id": movie.id,
                    "title": movie.title,
                    "year": getattr(movie, 'year', None),
                    "imdb_id": getattr(movie, 'imdb_id', None),
                    "type": getattr(movie, 'type', None),
                    "poster": getattr(movie, 'poster', None),
                    "imdb_rating": getattr(movie, 'imdb_rating', None)
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Movie not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
