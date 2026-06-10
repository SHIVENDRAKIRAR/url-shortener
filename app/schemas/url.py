from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    url: HttpUrl
    custom_alias: Optional[str] = None
    expires_in: Optional[int] = None  # days: 1, 7, 30, None=never

class URLResponse(BaseModel):
    id: int
    original_url: str
    short_url: str
    click_count: int
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_deleted: bool
    last_visited_at: Optional[datetime] = None
    status: Optional[str] = None  # "active", "expired", "deleted"

    class Config:
        from_attributes = True