import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
client = redis.from_url(REDIS_URL)

def get_cached_url(short_code: str):
    return client.get(short_code)

def set_cached_url(short_code: str, original_url: str, expiry_seconds: int = 3600):
    client.set(short_code, original_url, ex=expiry_seconds)