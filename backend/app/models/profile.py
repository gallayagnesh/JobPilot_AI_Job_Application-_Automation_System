from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base

class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    roles = Column(Text)
    skills = Column(Text)
    experience = Column(Integer)