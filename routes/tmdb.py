import httpx
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Movies, Reviews
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

def get_movie_details(movie_id: int, db: Session):
    movie = db.query(Movies).filter(Movies.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    reviews = db.query(Reviews).filter(Reviews.movie_id == movie_id).all()
    avg_rating = db.query(func.avg(Reviews.rating)).filter(Reviews.movie_id == movie_id).scalar()
    
    return {
        "id": movie.id,
        "title": movie.title,
        "year": movie.year,
        "imdb_id": movie.imdb_id,
        "type": movie.type,
        "poster": movie.poster,
        "imdb_rating": movie.imdb_rating,
        "average_rating": round(avg_rating, 2) if avg_rating else None,
        "total_reviews": len(reviews),
        "reviews": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "rating": r.rating,
                "review_text": r.review_text
            } for r in reviews
        ]
    }

def submit_review(movie_id: int, user_id: int, review_text: str, rating: int, db: Session):
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    if len(review_text) > 300:
        raise HTTPException(status_code=400, detail="Review text must be 300 characters or less")
    movie = db.query(Movies).filter(Movies.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    new_review = Reviews(
        movie_id=movie_id,
        user_id=user_id,
        review_text=review_text,
        rating=rating
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return {"message": "Review submitted successfully", "review_id": new_review.id}

def update_review(movie_id: int, review_id: int, user_id: int, review_text: str = None, rating: int = None, db: Session = None):
    review = db.query(Reviews).filter(
        Reviews.id == review_id,
        Reviews.movie_id == movie_id,
        Reviews.user_id == user_id
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    
    if rating is not None:
        if not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        review.rating = rating
    
    if review_text is not None:
        if len(review_text) > 300:
            raise HTTPException(status_code=400, detail="Review text must be 300 characters or less")
        review.review_text = review_text
    
    db.commit()
    db.refresh(review)
    
    return {"message": "Review updated successfully"}

def delete_review(movie_id: int, review_id: int, user_id: int, db: Session):
    review = db.query(Reviews).filter(
        Reviews.id == review_id,
        Reviews.movie_id == movie_id,
        Reviews.user_id == user_id
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found or not authorized")
    
    db.delete(review)
    db.commit()
    
    return {"message": "Review deleted successfully"}
