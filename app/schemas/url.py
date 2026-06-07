from pydantic import BaseModel , AnyHttpUrl


class URLCreate(BaseModel):
    url: AnyHttpUrl