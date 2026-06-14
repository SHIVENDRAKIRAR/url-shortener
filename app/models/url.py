from sqlalchemy import Column, Integer, String, DateTime , ForeignKey , Boolean
from datetime import datetime , timezone
from app.database import Base


class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=True)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    custom_alias = Column(String(50), nullable=True, unique=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    last_visited_at = Column(DateTime(timezone=True), nullable=True)