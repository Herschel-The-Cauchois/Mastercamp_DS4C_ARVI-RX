"""This file exists solely for the purpose of storing model classes and other Base models outside of the main file."""
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import *
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime

# Database setup is done in this file, else the table models don't work
DATABASE_URL = "sqlite:///../sqlite/arvi_rx.db"
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
        allowed = {"normal", "suspected_opacity", "uncertain", "not_annotated"} # Not annotated for further label manual confirmation
        if value not in allowed:
            raise ValueError(f"ground_truth_label must be among {allowed}")
        return value
    
    @field_validator("split")
    @classmethod
    def validate_split(cls, value):
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

class Prompts(Base): # Add prompting display and add interface ?
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

class PromptsCreate(BaseModel):
    name : str
    version : str
    content : str

    # Validators to insert

class PromptsResponse(BaseModel):
    id : int
    name : str
    version : str
    content : str
    created_at : datetime

class Runs(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey(Case.id), nullable=False) # Replace redundant info for normalization purposes by foreign key references
    prompt_id = Column(Integer, ForeignKey(Prompts.id), nullable=False)
    model_used = Column(String(50))
    prediction_json = Column(Text)
    predicted_class = Column(String(50))
    confidence = Column(Float)
    latency = Column(Float) # Float at a fex decimal rounded for more accuracy measurment
    created_at = Column(DateTime, default=datetime.now())

class RunsCreate(BaseModel):
    case_id : int
    prompt_id : int
    model_used : str
    prediction_json : str
    predicted_class : str
    confidence : float
    latency : float

    # Validators here

class RunsResponse(BaseModel):
    id : int
    case_id : int
    prompt_id : int
    model_used : str
    prediction_json : str
    predicted_class : str
    confidence : float
    latency : float
    created_at : datetime

class Evaluations(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey(Runs.id), nullable=False)
    true_label_case = Column(Integer, ForeignKey(Case.id), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    error_type = Column(String(64))
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.now())

class EvaluationsCreate(BaseModel):
    run_id : int
    true_label_case : int
    is_correct : bool
    error_type : str
    comments : str

    # Validators here

class EvaluationsResponse(BaseModel):
    id : int
    run_id : int
    true_label_case : int
    is_correct : bool
    error_type : str
    comments : str
    created_at : datetime

Base.metadata.create_all(bind=engine) # This line must always be last in order to be able to create and synchronize db schema

# Non db linked pydantic models

class AnalysisRequest(BaseModel):
    img_path : str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()