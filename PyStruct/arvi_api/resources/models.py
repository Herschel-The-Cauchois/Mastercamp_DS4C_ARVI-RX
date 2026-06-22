"""This file exists solely for the purpose of storing model classes and other Base models outside of the main file."""
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import *
from sqlalchemy import create_engine
from pathlib import Path

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

class CaseCreate(BaseModel):
    img_path : str
    source : str
    ground_truth_label : str
    split : str
    notes : str

    @field_validator("ground_truth_label")
    @classmethod
    def validate_label(cls, value):
        allowed = {"normal", "suspected_opacity", "uncertain"}
        if value not in allowed:
            raise ValueError(f"ground_truth_label must be among {allowed}")
        return value
    
    @field_validator("split")
    @classmethod
    def validate_label(cls, value):
        allowed = {"train", "test"}
        if value not in allowed:
            raise ValueError(f"split must be among {allowed}")
        return value
    
    @field_validator("img_path")
    @classmethod
    def validate_path(cls, value):
        try:
            Path(value).resolve(strict=False) # no need to make it check if the path really exists ?
            if Path(value).suffix.lower() not in {".jpg", ".jpeg", ".png"}: # File type check
                raise ValueError(f"{value} does not have an allowed extension.")
            return value
        except (OSError):
            raise ValueError(f"{value} is not a path.")


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