from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.url import URL
from app.schemas.url import URLCreate
from app.utils.base62 import encode
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.post("/shorten")
def shorten_url(
    payload: URLCreate,
    db: Session = Depends(get_db)
):
    # Create DB object
    new_url = URL(
        original_url=payload.url
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
        "url": new_url.original_url,
        "short_code": f"http://127.0.0.1:8000/{new_url.short_code}"
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
        return {"error": "Short URL not found"}

    url_entry.click_count += 1
    db.commit()

    return RedirectResponse(
        url=url_entry.original_url
    )