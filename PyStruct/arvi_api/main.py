from __future__ import annotations

import re
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from arvi_api.resources.models import *
from models.medgemma import MedGemma
from openai import APIConnectionError, InternalServerError, NotFoundError, BadRequestError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="EFREI Radiographical Pedagogical Analyzer", version="0.0.1")
app.mount("/uploads", StaticFiles(directory="../data/uploads"), name="uploads") # Exposes folder so uploads can be displayed on feedback
UPLOAD_DIR = Path("tmp_uploads")

origins = ["http://localhost:5173"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

model = MedGemma() # Initializes model relay for the API

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
        raise HTTPException(status_code=406, detail="Item does not match validation criterions : " + str(e))
    
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

@app.post("/analyze/")
async def jarvis_analyzer(item: AnalysisRequest): # "jarvis, analyze my radiography"
    try:
        with open("./models/prompt.txt", "r") as file:
            prompt = file.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Missing internal prompt file.")
    path_dump = dict(**item.model_dump())["img_path"]
    try: 
        response = model.generate(path_dump, prompt)
    except FileNotFoundError:
        raise HTTPException(status_code=412, detail="File has not been transferred to the server.")
    except APIConnectionError:
        raise HTTPException(status_code=503, detail="Medgemma API is not accessible.")
    except InternalServerError:
        raise HTTPException(status_code=503, detail="Medgemma API returned service unavailable")
    except NotFoundError:
        raise HTTPException(status_code=503, detail="Medgemma API returned Not Found Error")
    except BadRequestError:
        raise HTTPException(status_code=503, detail="Medgemma API endpoint is paused")
    return response

@app.put("/analyze/") # image file uploading
async def upload_file(file: UploadFile = File(...)):
    # print(file.filename)
    # print(file.content_type) test

    if file.content_type != "image/png":
        raise HTTPException(status_code=422, detail="Only png images are accepted for this app.")

    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=422, detail="Unable to read file.")
    
    try:
        with open("../data/uploads/"+file.filename, "wb") as upload:
            file.file.seek(0) # Puts cursor back at start of the file after reading
            shutil.copyfileobj(file.file, upload)
    except OSError as error:
        raise HTTPException(status_code=500, detail="File could not be uploaded correctly server side : " + str(error))

    return { "filename": file.filename, "size": len(contents), "status": "OK" }