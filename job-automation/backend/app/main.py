from fastapi import FastAPI
from app.api import resume

app = FastAPI()

app.include_router(resume.router)