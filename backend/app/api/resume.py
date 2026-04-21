from fastapi import APIRouter
from app.services.resume_ai import load_profile, generate_tailored_resume
from app.services.pdf_generator import save_resume_pdf

router = APIRouter()

@router.post("/generate-resume")
def generate_resume(job_description: str):

    profile = load_profile()
    tailored = generate_tailored_resume(job_description, profile)

    pdf_path = save_resume_pdf(tailored, "resume_output")

    return {
        "resume_text": tailored,
        "pdf_path": pdf_path
    }
