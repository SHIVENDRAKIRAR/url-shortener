from upstash_redis import Redis
from app.utils.logger import logger

client = Redis.from_env()

def get_cached_url(short_code: str):
    try:
        return client.get(short_code)
    except Exception as e:
        logger.warning(f"Redis get failed: {e}")
        return None

def set_cached_url(short_code: str, original_url: str, expiry_seconds: int = 3600):
    try:
        client.set(short_code, original_url, ex=expiry_seconds)
    except Exception as e:
        logger.warning(f"Redis set failed: {e}")
def delete_cached_url(short_code: str):
    try:
        client.delete(short_code)  
    except Exception as e:
        logger.warning(f"Redis delete failed: {e}")