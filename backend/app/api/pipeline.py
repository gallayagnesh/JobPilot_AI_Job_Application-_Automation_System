from fastapi import APIRouter
from app.services.pipeline import process_job

router = APIRouter()

@router.post("/process-job")
def process(job_description: str, source: str = "MANUAL"):
    return process_job(job_description, source=source)
