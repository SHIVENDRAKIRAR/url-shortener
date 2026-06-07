from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.url import URL
from app.schemas.url import URLCreate
from app.utils.base62 import encode
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()
load_dotenv()
BASE_URL = BASE_URL = os.getenv("BASE_URL")
@router.post("/shorten")
def shorten_url(
    payload: URLCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_url = URL(
        original_url=str(payload.url),
        user_id=current_user.id
    )

    # Save to database
    db.add(new_url)
    db.commit()

    # Get latest DB values (especially generated id)
    db.refresh(new_url)

    # Generate short code
    short_code = encode(new_url.id)

    # Update object
    new_url.short_code = short_code

    # Save update to DB
    db.commit()

    return {
        "id": new_url.id,
        "original_url": new_url.original_url,
        "short_url": f"{BASE_URL}/{new_url.short_code}",
        "click_count": new_url.click_count,
        "created_at": new_url.created_at
    }


@router.get("/{short_code}")
def redirect_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    url_entry = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    url_entry.click_count += 1
    db.commit()

    return RedirectResponse(
        url=url_entry.original_url
    )