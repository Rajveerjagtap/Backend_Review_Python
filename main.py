from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, UserLogin, UserRegister, Movies, Reviews, WriteReview, UpdateReview
from utils import encode, get_db, jwt_required
from database import engine, Base
from routes.auth import register_user, login_user
from routes.tmdb import (
    search, 
    get_movie_details, 
    submit_review, 
    update_review, 
    delete_review
)

app = FastAPI(
    title="Movie Review Aggregator API",
    description="An API for aggregating movie reviews and ratings",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

register_user(app)
login_user(app)

@app.get("/")
async def root():
    return {"message": "Movie Review API is running!"}


@app.get("/search/{title}")
async def search_movie(title: str, db: Session = Depends(get_db), user_id: int = Depends(jwt_required)):
    """Search for movies by title with review highlights"""
    try:
        movie = search(title, db)
        if movie:
            reviews = db.query(Reviews).filter(Reviews.movie_id == movie.id).limit(3).all()
            avg_rating = db.query(func.avg(Reviews.rating)).filter(Reviews.movie_id == movie.id).scalar()
            
            return {
                "success": True,
                "movie": {
                    "id": movie.id,
                    "title": movie.title,
                    "year": getattr(movie, 'year', None),
                    "imdb_id": getattr(movie, 'imdb_id', None),
                    "type": getattr(movie, 'type', None),
                    "poster": getattr(movie, 'poster', None),
                    "imdb_rating": getattr(movie, 'imdb_rating', None),
                    "average_rating": round(avg_rating, 2) if avg_rating else None,
                    "review_highlights": [
                        {
                            "user_id": r.user_id,
                            "rating": r.rating,
                            "review_text": r.review_text[:100] + "..." if len(r.review_text) > 100 else r.review_text
                        } for r in reviews
                    ]
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Movie not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/movies/{movie_id}")
async def movie_details(movie_id: int, db: Session = Depends(get_db), user_id: int = Depends(jwt_required)):
    """Retrieve details about a specific movie with its reviews"""
    return get_movie_details(movie_id, db)

@app.post("/movies/{movie_id}/reviews")
async def add_review(
    movie_id: int, 
    review: WriteReview = Body(...), 
    db: Session = Depends(get_db), 
    user_id: int = Depends(jwt_required)
):
    return submit_review(
        movie_id=movie_id,
        user_id=user_id,
        review_text=review.review_text,
        rating=review.rating,
        db=db
    )

@app.put("/movies/{movie_id}/reviews/{review_id}")
async def edit_review(
    movie_id: int,
    review_id: int,
    update: UpdateReview = Body(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(jwt_required)
):
    """Update a specific review"""
    return update_review(
        movie_id=movie_id,
        review_id=review_id,
        user_id=user_id, 
        review_text=update.review_text,
        rating=update.rating,
        db=db
    )

@app.delete("/movies/{movie_id}/reviews/{review_id}")
async def remove_review(
    movie_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(jwt_required)
):
    """Delete a specific review"""
    return delete_review(movie_id, review_id, user_id, db)

@app.get("/user/profile")
async def user_profile(db: Session = Depends(get_db), user_id: int = Depends(jwt_required)):
    """Get user profile with all submitted reviews"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reviews = db.query(Reviews).filter(Reviews.user_id == user_id).all()
    
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "total_reviews": len(reviews),
        "reviews": [
            {
                "id": r.id,
                "movie_id": r.movie_id,
                "movie_title": r.movie.title,
                "rating": r.rating,
                "review_text": r.review_text
            } for r in reviews
        ]
    }



