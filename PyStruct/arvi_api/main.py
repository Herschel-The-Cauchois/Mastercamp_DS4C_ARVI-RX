from __future__ import annotations

import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from arvi_api.resources.models import *
from arvi_api.resources.validators import *
from arvi_api.resources.responses import *
from models.medgemma import MedGemma
from openai import APIConnectionError, InternalServerError, NotFoundError, BadRequestError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from hashlib import sha256
from jose import JWTError, jwt

app = FastAPI(title="EFREI Radiographical Pedagogical Analyzer", version="0.0.1")
app.mount("/uploads", StaticFiles(directory="../data/uploads"), name="uploads") # Exposes folder so uploads can be displayed on feedback
UPLOAD_DIR = Path("../data/uploads/")
SECRET_KEY = "Oooodelalyyyyyy, oooodelalooooooo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

origins = ["http://localhost:5173"]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

model = MedGemma() # Initializes model relay for the API

@app.get("/")
def root() -> dict:
    return {"status": "OK", "scope": "DO NOT USE FOR MEDICAL DIAGNOSIS, THIS IS A PROJECT FOR EDUCATIONAL PURPOSES"}

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
    
@app.get("/case/req", response_model=CaseResponse) # Sadly contrary to node, fastapi doesn't support http keywords other than PUT, POST, GET, DELETE
async def lookup_case(path: str, db: Session = Depends(get_db)):
    try:
        element = db.query(Case).filter(Case.img_path == path).first() # Try to retrieve first element whose path matches with sent patch
        if element is None:
            raise HTTPException(status_code=404, detail="Case match corresponding to duplicate path not found.")
        return element
    except BaseException as e:
        raise HTTPException(status_code=500, detail="An unknown error has occured : " + e)
    
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

@app.get("/eval/")
async def request_eval(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT evals.id, evals.run_id, cases.ground_truth_label, cases.img_path, runs.model_used, runs.confidence, runs.latency, evals.is_correct, evals.error_type, evals.comments FROM \"evaluations\" AS evals INNER JOIN \"runs\" AS runs ON evals.run_id = runs.id INNER JOIN \"case\" AS cases ON evals.true_label_case = cases.id ORDER BY evals.error_type, evals.created_at;")).mappings().all() # Omega long sql request it wouldn't been hard to translate in python
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error with your request has happened : " + str(e))
    
@app.patch("/eval/")
async def update_eval(item: EvaluationsUpdate, db: Session = Depends(get_db)):
    try:
        new_data = dict(**item.model_dump())
        query = text("""UPDATE evaluations SET is_correct = :is_correct, error_type = :error_type, comments = :comments WHERE id = :id;""")
        result = db.execute(query, { "is_correct": new_data["new_correct"], "error_type": new_data["new_type"], "comments": new_data["new_comment"], "id": new_data["id"] })
        db.commit() # DO NOT FORGET !!!!! else doesn't save
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error with your request has happened : " + str(e)) 
    
@app.delete("/eval/")
async def delete_eval(item: EvaluationsUpdate, db: Session = Depends(get_db)):
    try:
        del_data = dict(**item.model_dump())
        query_fetch = text("SELECT run_id FROM evaluations WHERE id = :id")
        query_eval = text("DELETE FROM evaluations WHERE id = :id")
        query_run = text("DELETE FROM runs WHERE id = :id")
        result1 = db.execute(query_fetch, { "id": del_data["id"] }).mappings().all()
        print(result1)
        result2 = db.execute(query_run,  { "id": result1[0]["run_id"] }) # Always one lone tuple in a list anyway
        result3 = db.execute(query_eval, { "id": del_data["id"] })
        db.commit()
        return [result1, result2, result3]
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error with your request has happened : " + str(e))

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
    except NotFoundError as e:
        raise HTTPException(status_code=503, detail="Medgemma API returned Not Found Error : " + str(e))
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
    
    override_path = "" # Addendum to differenciate duplicates in name but not in content
    msg = ""
    
    try:
        with open("../data/uploads/"+file.filename, "rb") as match:
            file.file.seek(0)
            passover_var = match.read()
            if passover_var == contents:
                msg = "Duplicate" # Sends special message for front to handle
            else:
                override_path = "_" + datetime.now().strftime("%y-%m-%D_%H-%M-%S")
    except FileNotFoundError:
        try:
            with open("../data/uploads/"+file.filename+override_path, "wb") as upload:
                file.file.seek(0) # Puts cursor back at start of the file after reading
                shutil.copyfileobj(file.file, upload)
        except OSError as error:
            raise HTTPException(status_code=500, detail="File could not be uploaded correctly server side : " + str(error))

    return { "filename": file.filename, "size": len(contents), "status": "OK" if msg == "" else msg }

@app.get("/analyze/")
async def retrieve_file(path: str):
    try:
        fp = Path(path)
        if not fp.resolve().is_relative_to(UPLOAD_DIR.resolve()):
            raise HTTPException(status_code=403, detail="Given path not in expected directory")
        if not fp.exists():
            raise HTTPException(status_code=404, detail="File not found")
        filename = path.split("/")
        filename = filename[len(filename)-1]
        return FileResponse(fp, filename=filename, media_type="image/png") 
    except HTTPException as HTTP: # Pass HTTP exceptions as already handled...
        raise HTTPException(HTTP.status_code, detail=HTTP.detail)
    except Exception as e: # To handle then all other types
        raise HTTPException(status_code=500, detail="An unknown error has occured : " + str(e))
    
@app.put("/users/")
async def create_user(item: UserCreate, db: Session = Depends(get_db)):
    try:
        db_item = dict(**item.model_dump())
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        prehash = sha256(db_item["password"].encode("utf-8")).hexdigest()
        db_item["password"] = pwd_context.hash(prehash)
        db_item = Users(**db_item)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unknown error has occured : " + str(e))

@app.post("/users/", response_model=AuthResponse)
async def check_credentials(credentials: CredentialsRequest, db: Session = Depends(get_db)):
    try:
        to_check = dict(**credentials.model_dump())
        query = text("SELECT * FROM users WHERE email = :email")
        user = db.execute(query, { "email": to_check["email"] })
        if user.cursor.description is None:
            raise HTTPException(status_code=500, detail="Query did not return an expected result set.")
        user = user.first()  # Check if there is a result set, if there's nothing in it
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        user = user._mapping # dictionary conversion time
        pwd_context = CryptContext(schemes=["argon2"], deprecated="auto") # Hash comparison testing time
        prehash = sha256(to_check["password"].encode("utf-8")).hexdigest()
        if not pwd_context.verify(prehash,user["password"]):
            raise HTTPException(status_code=401, detail="Invalid password.")
        if user["is_valid"] == 0:
            raise HTTPException(status_code=403, detail="Expired Credentials")
        try:
            data = { "id": user["id"] }
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return { "token": encoded_jwt }
        except JWTError as e:
            raise HTTPException(status_code=500, detail="Caramba ! JWT token encryption went wrong.")
    except HTTPException as HTTP:
        raise HTTPException(status_code=HTTP.status_code, detail=HTTP.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error has occured : " + str(e))