from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.url import URL
from app.schemas.url import URLCreate, URLResponse
from app.utils.base62 import encode
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from app.utils.auth import get_current_user
from app.models.user import User
from app.utils.limiter import limiter
import os
from app.utils.cache import get_cached_url, set_cached_url
from app.utils.logger import logger

router = APIRouter()
load_dotenv()
BASE_URL = os.getenv("BASE_URL")


@router.get("/my-urls", response_model=list[URLResponse])
def my_urls(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    urls = db.query(URL).filter(URL.user_id == current_user.id).all()
    return [
        {
            "id": u.id,
            "original_url": u.original_url,
            "short_url": f"{BASE_URL}/{u.short_code}",
            "click_count": u.click_count,
            "created_at": u.created_at
        }
        for u in urls
    ]


@router.post("/shorten", response_model=URLResponse)
@limiter.limit("5/minute")
def shorten_url(
    request: Request,
    payload: URLCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_url = URL(
        original_url=str(payload.url),
        user_id=current_user.id
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    short_code = encode(new_url.id)
    new_url.short_code = short_code
    db.commit()

    return {
        "id": new_url.id,
        "original_url": new_url.original_url,
        "short_url": f"{BASE_URL}/{new_url.short_code}",
        "click_count": new_url.click_count,
        "created_at": new_url.created_at
    }


from app.utils.cache import get_cached_url, set_cached_url

@router.get("/{short_code}")
def redirect_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    # Check Redis first
    cached = get_cached_url(short_code)
    if cached:
        logger.info(f"Cache HIT: {short_code}")
        return RedirectResponse(url=cached)

    # Not in cache — hit DB
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Save to Redis for next time
    set_cached_url(short_code, url_entry.original_url)

    url_entry.click_count += 1
    db.commit()
    logger.info(f"Cache MISS: {short_code} — querying DB")

    return RedirectResponse(url=url_entry.original_url)