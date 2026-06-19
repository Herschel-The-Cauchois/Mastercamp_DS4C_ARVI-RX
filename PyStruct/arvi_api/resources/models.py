"""This file exists solely for the purpose of storing model classes and other Base models outside of the main file."""
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

# Database setup is done in this file, else the table models don't work
DATABASE_URL = "sqlite:///../../sqlite/arvi_rx.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

Base.metadata.create_all(bind=engine)

class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)
    test = Column(String, index=True)

class TestCreate(BaseModel):
    test: str

class TestResponse(BaseModel):
    id: int
    test: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()