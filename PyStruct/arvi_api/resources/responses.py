from pydantic import BaseModel
from datetime import datetime

class CaseResponse(BaseModel):
    id : int
    img_path : str
    source : str
    ground_truth_label : str
    split : str
    notes : str

class PromptsResponse(BaseModel):
    id : int
    name : str
    version : str
    content : str
    created_at : datetime

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

class EvaluationsResponse(BaseModel):
    id : int
    run_id : int
    true_label_case : int
    is_correct : bool
    error_type : str
    comments : str
    created_at : datetime

class UserResponse(BaseModel):
    id : int
    email : str
    password : str
    is_valid : int

class AuthResponse(BaseModel):
    token : str