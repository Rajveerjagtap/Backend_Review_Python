import httpx
from sqlalchemy.orm import Session
from models import Movies
from fastapi import HTTPException

TMDB_API_KEY = "891026a09021ffc1953e8cd6c55db4a1"  
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def fetch_movie_from_tmdb(title: str):
    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }
    response = httpx.get(f"{TMDB_BASE_URL}/search/movie", params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="TMDb API error")
    results = response.json().get("results")
    if not results:
        return None
    movie_data = results[0]
    movie_id = movie_data["id"]
    details_resp = httpx.get(f"{TMDB_BASE_URL}/movie/{movie_id}", params={"api_key": TMDB_API_KEY})
    if details_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="TMDb API error")
    details = details_resp.json()

    imdb_id = details.get("imdb_id")
    if not imdb_id:
        ext_resp = httpx.get(f"{TMDB_BASE_URL}/movie/{movie_id}/external_ids", params={"api_key": TMDB_API_KEY})
        if ext_resp.status_code == 200:
            imdb_id = ext_resp.json().get("imdb_id")
    if not imdb_id:
        raise HTTPException(status_code=404, detail="IMDB ID not found for this movie.")

    return {
        "title": details["title"],
        "year": details.get("release_date", "")[:4],
        "imdb_id": imdb_id,
        "type": "movie",
        "poster": f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get("poster_path") else None,
        "imdb_rating": str(details.get("vote_average", ""))
    }

def search(title: str, db: Session):
    movie = db.query(Movies).filter(Movies.title.ilike(f"%{title}%")).first()
    if movie:
        return movie
    movie_data = fetch_movie_from_tmdb(title)
    if not movie_data:
        return None
    new_movie = Movies(**movie_data)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie