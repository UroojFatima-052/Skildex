from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobPostingCreate(BaseModel):
    title: str
    company: Optional[str] = None
    raw_description: str
    source: Optional[str] = "manual"

class JobPostingResponse(BaseModel):
    id: int
    title: str
    company: Optional[str]
    raw_description: str
    source: Optional[str]
    scraped_at: datetime

    class Config:
        from_attributes = True