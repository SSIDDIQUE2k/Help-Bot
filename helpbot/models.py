from pydantic import BaseModel
from typing import List, Optional

class AnalyzeRequest(BaseModel):
    error_text: str

class AnalyzeResponse(BaseModel):
    issue: str
    explanation: str
    resolution: Optional[str]
    source_title: str
    source_url: str 