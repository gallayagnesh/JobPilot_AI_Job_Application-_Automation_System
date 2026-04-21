from fastapi import FastAPI
from app.api import jobs, pipeline, resume
from app.db.database import Base, engine, ensure_sqlite_schema
from app.models import job, application, profile

Base.metadata.create_all(bind=engine)
ensure_sqlite_schema()

app = FastAPI()

app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(pipeline.router)
