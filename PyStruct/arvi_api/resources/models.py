"""This file exists solely for the purpose of storing model classes and other Base models outside of the main file."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import *
from datetime import datetime
from sqlalchemy import create_engine

# Database setup is done in this file, else the table models don't work
DATABASE_URL = "sqlite:///../sqlite/arvi_rx.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Case(Base):
    __tablename__ = "case"
    id = Column(Integer, primary_key=True, index=True)
    img_path = Column(Text)
    source = Column(Text, index=True)
    ground_truth_label = Column(String(50))
    split = Column(String(50))
    notes = Column(Text)

class Prompts(Base): # Add prompting display and add interface ?
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now())

class Runs(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey(Case.id), nullable=False) # Replace redundant info for normalization purposes by foreign key references
    prompt_id = Column(Integer, ForeignKey(Prompts.id), nullable=False)
    model_used = Column(String(50))
    prediction_json = Column(Text, nullable=False)
    predicted_class = Column(String(50), nullable=False)
    confidence = Column(Float)
    latency = Column(Float) # Float at a fex decimal rounded for more accuracy measurment
    created_at = Column(DateTime, default=datetime.now())

class Evaluations(Base):
    __tablename__ = "evaluations"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey(Runs.id), nullable=False)
    true_label_case = Column(Integer, ForeignKey(Case.id), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    error_type = Column(String(64))
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.now())

Base.metadata.create_all(bind=engine) # This line must always be last in order to be able to create and synchronize db schema

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()