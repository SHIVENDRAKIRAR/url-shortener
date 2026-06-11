import io
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.url import URL
from app.models.user import User
from app.schemas.url import URLCreate, URLResponse
from app.utils.auth import get_current_user, get_optional_user
from app.utils.base62 import generate_short_code
from app.utils.cache import delete_cached_url, get_cached_url, set_cached_url
from app.utils.limiter import limiter
from app.utils.logger import logger

router = APIRouter(tags=["urls"])

BASE_URL = os.getenv("BASE_URL")

RESERVED_ALIASES = {
    "login", "register", "docs", "openapi.json",
    "my-urls", "auth", "admin", "shorten", "urls",
}


# ── Helpers ──────────────────────────────────────────────────

def compute_status(u: URL) -> str:
    if u.is_deleted:
        return "deleted"
    if u.expires_at and u.expires_at < datetime.now(timezone.utc):
        return "expired"
    return "active"


def url_to_response(u: URL) -> dict:
    return {
        "id": u.id,
        "original_url": u.original_url,
        "short_url": f"{BASE_URL}/{u.short_code}",
        "click_count": u.click_count,
        "created_at": u.created_at,
        "expires_at": u.expires_at,
        "is_deleted": u.is_deleted,
        "last_visited_at": u.last_visited_at,
        "status": compute_status(u),
    }


def get_unique_short_code(db: Session) -> str:
    """Generate a Base62 short code that doesn't already exist in DB."""
    while True:
        code = generate_short_code()
        if not db.query(URL).filter(URL.short_code == code).first():
            return code


# ── Dashboard ────────────────────────────────────────────────

@router.get("/my-urls", response_model=list[URLResponse])
def my_urls(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return paginated list of URLs for the logged-in user."""
    skip = (page - 1) * limit
    urls = (
        db.query(URL)
        .filter(URL.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [url_to_response(u) for u in urls]


# ── Shorten ──────────────────────────────────────────────────

@router.post("/shorten", response_model=URLResponse)
@limiter.limit("5/minute")
def shorten_url(
    request: Request,
    payload: URLCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Shorten a URL.
    - Guest: works without login, auto-expires in 24h, no custom alias/expiry.
    - Logged in: custom alias, custom expiry, deduplication, never-expire default.
    """
    now = datetime.now(timezone.utc)
    is_guest = current_user is None

    # Guest restrictions
    if is_guest and payload.custom_alias:
        raise HTTPException(status_code=401, detail="Login required for custom alias")
    if is_guest and payload.expires_in:
        raise HTTPException(status_code=401, detail="Login required for custom expiry")

    # Alias validation
    if payload.custom_alias:
        if payload.custom_alias in RESERVED_ALIASES:
            raise HTTPException(status_code=400, detail="Alias is reserved")
        if db.query(URL).filter(URL.custom_alias == payload.custom_alias).first():
            raise HTTPException(status_code=409, detail="Alias already taken")

    # Deduplication — skip if custom alias requested (user wants a new code)
    if not is_guest and not payload.custom_alias:
        existing = db.query(URL).filter(
            URL.original_url == str(payload.url),
            URL.user_id == current_user.id,
            URL.is_deleted == False,
        ).first()
        if existing:
            return url_to_response(existing)

    # Expiry
    if is_guest:
        expires_at = now + timedelta(hours=24)
    elif payload.expires_in:
        expires_at = now + timedelta(days=payload.expires_in)
    else:
        expires_at = None

    # Short code
    short_code = payload.custom_alias or get_unique_short_code(db)

    new_url = URL(
        original_url=str(payload.url),
        short_code=short_code,
        custom_alias=payload.custom_alias,
        user_id=current_user.id if not is_guest else None,
        expires_at=expires_at,
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return url_to_response(new_url)


# ── Redirect ─────────────────────────────────────────────────

@router.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    """Redirect to original URL. Validates expiry and deleted status on every hit."""
    cached = get_cached_url(short_code)
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()

    if cached:
        logger.info(f"Cache HIT: {short_code}")
    else:
        logger.info(f"Cache MISS: {short_code}")
        if url_entry:
            set_cached_url(short_code, url_entry.original_url)

    if not url_entry or url_entry.is_deleted:
        raise HTTPException(status_code=404, detail="Short URL not found")

    if url_entry.expires_at and url_entry.expires_at < datetime.now(timezone.utc):
        delete_cached_url(short_code)
        raise HTTPException(status_code=410, detail="Link has expired")

    url_entry.click_count += 1
    url_entry.last_visited_at = datetime.now(timezone.utc)
    db.commit()

    return RedirectResponse(url=url_entry.original_url, status_code=307)


# ── Delete ───────────────────────────────────────────────────

@router.delete("/urls/{url_id}")
def delete_url(
    url_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a URL. Sets is_deleted=True, redirect returns 404."""
    url_entry = db.query(URL).filter(
        URL.id == url_id,
        URL.user_id == current_user.id,
    ).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    url_entry.is_deleted = True
    db.commit()
    return {"message": "URL deleted successfully"}


# ── Stats ────────────────────────────────────────────────────

@router.get("/urls/{url_id}/stats", response_model=URLResponse)
def url_stats(
    url_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get click count, timestamps and status for a URL."""
    url_entry = db.query(URL).filter(
        URL.id == url_id,
        URL.user_id == current_user.id,
    ).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    return url_to_response(url_entry)


# ── QR Code ──────────────────────────────────────────────────

@router.get("/urls/{url_id}/qr")
def get_qr_code(
    url_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate and return a QR code PNG for the short URL."""
    url_entry = db.query(URL).filter(
        URL.id == url_id,
        URL.user_id == current_user.id,
    ).first()

    if not url_entry or url_entry.is_deleted:
        raise HTTPException(status_code=404, detail="URL not found")

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(f"{BASE_URL}/{url_entry.short_code}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")