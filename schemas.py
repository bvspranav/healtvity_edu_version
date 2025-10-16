from pydantic import BaseModel
from typing import Optional, List, Dict

class SymptomRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class SymptomResponse(BaseModel):
    conditions: List[Dict]  # e.g. [{"condition":"Asthma","prob":0.4, "notes":"..."}]
    recommendations: str
    follow_up: Optional[str]
    disclaimer: str
