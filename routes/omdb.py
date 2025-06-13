import httpx
from sqlalchemy.orm import Session
from models import Movies 

OMDB_API_KEY = "5b23f39e"
OMDB_URL = "http://www.omdbapi.com"

def search(title: str):
    params = {
        "t": title,
        "apikey": OMDB_API_KEY
    }
    response = httpx.get(OMDB_URL, params=params)
    data = response.json()
    if data.get("Response") == "False":
        return None
    return {
        "title": data["Title"],
        "year": data["Year"],
        "imdb_id": data["imdbID"],
        "type": data["Type"],
        "poster": data["Poster"],
        "imdb_rating": str(data.get("imdbRating", "0"))
    }



