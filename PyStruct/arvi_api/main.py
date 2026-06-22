from __future__ import annotations

import re
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from resources.models import *

app = FastAPI(title="EFREI Radiographical Pedagogical Analyzer", version="0.0.1")
UPLOAD_DIR = Path("tmp_uploads")

@app.get("/")
def root() -> dict:
    return {"status": "OK", "scope": "DO NOT USE FOR MEDICAL DIAGNOSIS, THIS IS A PROJECT FOR EDUCATIONAL PURPOSES"}

@app.post("/test/", response_model=TestResponse)
async def create_test(item: TestCreate, db: Session = Depends(get_db)):
    db_item = Test(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/case/", response_model=CaseResponse)
async def create_case(item: CaseCreate, db: Session = Depends(get_db)):
    try:
        db_item = Case(**item.model_dump())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except ValueError as e:
        raise HTTPException(status=406, detail="Item does not match validation criterions : " + str(e))
    
@app.post("/prompts/", response_model=PromptsResponse)
async def create_prompt(item: PromptsCreate, db: Session = Depends(get_db)):
    db_item = Prompts(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/runs/", response_model=RunsResponse)
async def create_run(item: RunsCreate, db: Session = Depends(get_db)):
    db_item = Runs(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.post("/eval/", response_model=EvaluationsResponse)
async def create_eval(item: EvaluationsCreate, db: Session = Depends(get_db)):
    db_item = Evaluations(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item