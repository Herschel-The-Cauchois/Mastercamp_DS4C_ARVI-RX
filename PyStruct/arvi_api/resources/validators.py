from pathlib import Path
import json
from pydantic import BaseModel, field_validator
import re

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
        
class PromptsCreate(BaseModel):
    name : str
    version : str
    content : str

    # Validators to insert

class RunsCreate(BaseModel):
    case_id : int
    prompt_id : int
    model_used : str
    prediction_json : str
    predicted_class : str
    confidence : float
    latency : float

    @field_validator("prediction_json")
    @classmethod
    def validate_json(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise TypeError("Provided JSON string is not a string.")  # String type test just in case    
        try:
            json.loads(value)  # Try parsing, if fails raise exception
            return value
        except json.JSONDecodeError:
            raise TypeError(f"{value} is not a correct JSON string.")
        
    @field_validator("predicted_class")
    @classmethod
    def validate_label(cls, value):
        allowed = {"normal", "suspected_opacity", "uncertain"} 
        if value not in allowed:
            raise ValueError(f"ground_truth_label must be among {allowed}")
        return value
    
class EvaluationsCreate(BaseModel):
    run_id : int
    true_label_case : int
    is_correct : bool
    error_type : str
    comments : str

class EvaluationsUpdate(BaseModel):
    id : int
    new_correct : int
    new_type : str
    new_comment : str

class UserCreate(BaseModel):
    email : str
    password : str # Bonus idea : password criterions
    is_valid : int

    @field_validator("email")
    @classmethod
    def email_validator(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise TypeError("Provided email is not a string.")
        if "@" not in value or "." not in value:
            raise ValueError("This email isn't an email adress with an @ and a domain.")
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(email_regex, value) is None:
            raise ValueError("Provided email is not formatted correctly to point towards a valid domain.")
        return value
    
    @field_validator("password")
    @classmethod
    def password_validator(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Password is empty.")
        return value # Not much here because this would be more accurate to do it on the front end


# Non db linked pydantic models

class AnalysisRequest(BaseModel):
    img_path : str

class CredentialsRequest(BaseModel):
    email : str
    password : str