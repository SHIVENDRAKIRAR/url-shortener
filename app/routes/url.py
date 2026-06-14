from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse
from app.utils.auth import get_current_user, get_optional_user
from app.utils.limiter import limiter
from app.services.url_service import (
    delete_url,
    generate_qr_code,
    get_url_stats,
    get_user_urls,
    redirect_url,
    shorten_url,
)

router = APIRouter(tags=["urls"])


@router.get("/my-urls", response_model=list[URLResponse])
def my_urls(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_urls(page, limit, current_user, db)


@router.post("/shorten", response_model=URLResponse)
@limiter.limit("5/minute")
def shorten_url_route(
    request: Request,
    payload: URLCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    return shorten_url(payload, db, current_user)


@router.get("/{short_code}")
def redirect_url_route(short_code: str, db: Session = Depends(get_db)):
    url = redirect_url(short_code, db)
    return RedirectResponse(url=url, status_code=307)


@router.delete("/urls/{url_id}")
def delete_url_route(
    url_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_url(url_id, current_user, db)


@router.get("/urls/{url_id}/stats", response_model=URLResponse)
def url_stats_route(
    url_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_url_stats(url_id, current_user, db)


@router.get("/urls/{url_id}/qr")
def get_qr_code_route(
    url_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    buf = generate_qr_code(url_id, current_user, db)
    return StreamingResponse(buf, media_type="image/png")