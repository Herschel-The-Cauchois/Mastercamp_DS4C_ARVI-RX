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
async def create_item(item: TestCreate, db: Session = Depends(get_db)):
    db_item = Test(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item