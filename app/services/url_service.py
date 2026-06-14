import io
from datetime import datetime, timedelta, timezone
from typing import Optional

import qrcode
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.url import URL
from app.models.user import User
from app.schemas.url import URLCreate
from app.utils.base62 import generate_short_code
from app.utils.cache import delete_cached_url, get_cached_url, set_cached_url
from app.utils.logger import logger


RESERVED_ALIASES = {
    "login", "register", "docs", "openapi.json",
    "my-urls", "auth", "admin", "shorten", "urls",
}



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
        "short_url": f"{settings.BASE_URL}/{u.short_code}",
        "click_count": u.click_count,
        "created_at": u.created_at,
        "expires_at": u.expires_at,
        "is_deleted": u.is_deleted,
        "last_visited_at": u.last_visited_at,
        "status": compute_status(u),
    }


def get_unique_short_code(db: Session) -> str:
    while True:
        code = generate_short_code()
        if not db.query(URL).filter(URL.short_code == code).first():
            return code



def get_user_urls(
    page: int,
    limit: int,
    current_user: User,
    db: Session,
) -> list[dict]:
    skip = (page - 1) * limit
    urls = (
        db.query(URL)
        .filter(URL.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [url_to_response(u) for u in urls]


def shorten_url(
    payload: URLCreate,
    db: Session,
    current_user: Optional[User],
) -> dict:
    now = datetime.now(timezone.utc)
    is_guest = current_user is None

    if is_guest and payload.custom_alias:
        raise HTTPException(status_code=401, detail="Login required for custom alias")
    if is_guest and payload.expires_in:
        raise HTTPException(status_code=401, detail="Login required for custom expiry")

    if payload.custom_alias:
        if payload.custom_alias in RESERVED_ALIASES:
            raise HTTPException(status_code=400, detail="Alias is reserved")
        if db.query(URL).filter(URL.custom_alias == payload.custom_alias).first():
            raise HTTPException(status_code=409, detail="Alias already taken")

    if not is_guest and not payload.custom_alias:
        existing = db.query(URL).filter(
            URL.original_url == str(payload.url),
            URL.user_id == current_user.id,
            URL.is_deleted == False,
        ).first()
        if existing:
            return url_to_response(existing)

    if is_guest:
        expires_at = now + timedelta(hours=24)
    elif payload.expires_in:
        expires_at = now + timedelta(days=payload.expires_in)
    else:
        expires_at = None

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


def redirect_url(short_code: str, db: Session) -> str:
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

    return url_entry.original_url


def delete_url(url_id: int, current_user: User, db: Session) -> dict:
    url_entry = db.query(URL).filter(
        URL.id == url_id,
        URL.user_id == current_user.id,
    ).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    url_entry.is_deleted = True
    db.commit()
    return {"message": "URL deleted successfully"}


def get_url_stats(url_id: int, current_user: User, db: Session) -> dict:
    url_entry = db.query(URL).filter(
        URL.id == url_id,
        URL.user_id == current_user.id,
    ).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    return url_to_response(url_entry)


def generate_qr_code(url_id: int, current_user: User, db: Session) -> io.BytesIO:
    url_entry = db.query(URL).filter(
        URL.id == url_id,
        URL.user_id == current_user.id,
    ).first()

    if not url_entry or url_entry.is_deleted:
        raise HTTPException(status_code=404, detail="URL not found")

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(f"{settings.BASE_URL}/{url_entry.short_code}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf