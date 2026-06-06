from pydantic import BaseModel


class URLCreate(BaseModel):
    url: str