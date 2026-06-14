import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BASE_URL: str

    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY", "")
        self.BASE_URL = os.getenv("BASE_URL", "")

        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY not found in environment")
        if not self.BASE_URL:
            raise ValueError("BASE_URL not found in environment")


settings = Settings()