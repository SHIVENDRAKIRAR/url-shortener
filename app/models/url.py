from sqlalchemy import Column, Integer, String, DateTime , ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime , timezone

Base = declarative_base()


class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=True)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)