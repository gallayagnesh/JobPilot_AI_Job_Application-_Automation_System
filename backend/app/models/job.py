from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company = Column(String)
    description = Column(Text)
    link = Column(String)
    fingerprint = Column(String, index=True)
    source = Column(String, default="MANUAL")
    resume_path = Column(String)
    tracking_status = Column(String, default="NEW")
    times_seen = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())

    semantic_score = Column(Float)
    constraint_score = Column(Float)
    final_score = Column(Float)
    decision = Column(String)
