from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from app.db.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer)
    resume_path = Column(String)
    status = Column(String, default="PENDING")
    applied_at = Column(DateTime(timezone=True), server_default=func.now())