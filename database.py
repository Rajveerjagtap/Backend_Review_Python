from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

DATABASE_URL = "postgresql://movies_review:moviespass@localhost:5432/movie_review_db"  

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
