from upstash_redis import Redis
from app.utils.logger import logger

client = Redis.from_env()

def get_cached_url(short_code: str):
    return client.get(short_code)

def set_cached_url(short_code: str, original_url: str, expiry_seconds: int = 3600):
    client.set(short_code, original_url, ex=expiry_seconds)

def delete_cached_url(short_code: str):
    try:
        client.delete(short_code)  # client, not redis
    except Exception as e:
        logger.warning(f"Redis delete failed: {e}")