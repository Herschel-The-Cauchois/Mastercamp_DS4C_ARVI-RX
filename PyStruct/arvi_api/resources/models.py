"""This file exists solely for the purpose of storing model classes and other Base models outside of the main file."""
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import *
from sqlalchemy import create_engine

# Database setup is done in this file, else the table models don't work
DATABASE_URL = "sqlite:///../../sqlite/arvi_rx.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Test(Base): # Dummy, to be removed once all models done and working
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, index=True)
    test = Column(String, index=True)

class TestCreate(BaseModel):
    test: str

class TestResponse(BaseModel):
    id: int
    test: str

class Case(Base):
    __tablename__ = "case"
    id = Column(Integer, primary_key=True, index=True)
    img_path = Column(Text)
    source = Column(Text, index=True)
    ground_truth_label = Column(String(50))
    split = Column(String(50))
    notes = Column(Text)

    # Put validators with @validates decorator
    # To do : ground_truth label between several values, idem split, img path must be valid, source must be link

class CaseCreate(BaseModel):
    img_path : str
    source : str
    ground_truth_label : str
    split : str
    notes : str

class CaseResponse(BaseModel):
    id : int
    img_path : str
    source : str
    ground_truth_label : str
    split : str
    notes : str

Base.metadata.create_all(bind=engine) # This line must always be last in order to be able to create and synchronize db schema

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()