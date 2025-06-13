import httpx
from sqlalchemy.orm import Session
from models import Movies 

import requests

TMDB_API_KEY = "891026a09021ffc1953e8cd6c55db4a1" 
BASE_URL = "https://api.themoviedb.org/3"

def get_tmdb_data(endpoint, params=None):
    params = params or {}
    params['api_key'] = TMDB_API_KEY
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    return response.json()

def search(title: str, db_session: Session):
    # First check if movie exists in local database
    movie = db_session.query(Movies).filter(Movies.title.ilike(f"%{title}%")).first()
    if movie:
        return movie
    
    tmdb_data = get_tmdb_data("search/movie", {"query": title})
    if tmdb_data and tmdb_data.get("results"):
        movie_data = tmdb_data["results"][0] 
        
        year = None
        if movie_data.get("release_date"):
            year = movie_data["release_date"][:4]
        
        new_movie = Movies(
            title=movie_data["title"],
            year=year,
            imdb_id=str(movie_data["id"]),  
            type="movie",
            poster=f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}" if movie_data.get('poster_path') else None,
            imdb_rating=str(movie_data.get("vote_average", ""))
        )
        db_session.add(new_movie)
        db_session.commit()
        db_session.refresh(new_movie)
        return new_movie

    return None


