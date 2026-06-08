from upstash_redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()

client = Redis.from_env()

def get_cached_url(short_code: str):
    return client.get(short_code)

def set_cached_url(short_code: str, original_url: str, expiry_seconds: int = 3600):
    client.set(short_code, original_url, ex=expiry_seconds)