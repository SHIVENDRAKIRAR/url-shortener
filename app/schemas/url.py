from pydantic import BaseModel, AnyHttpUrl
from datetime import datetime

class URLCreate(BaseModel):
    url: AnyHttpUrl

class URLResponse(BaseModel):
    id: int
    original_url: str
    short_url: str
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True