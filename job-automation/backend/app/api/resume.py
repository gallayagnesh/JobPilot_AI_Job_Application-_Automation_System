from fastapi import APIRouter
from app.services.resume_ai import load_master_resume, generate_tailored_resume
from app.services.pdf_generator import save_resume_pdf

router = APIRouter()

@router.post("/generate-resume")
def generate_resume(job_description: str):

    master = load_master_resume()

    tailored = generate_tailored_resume(job_description, master)

    pdf_path = save_resume_pdf(tailored, "resume_output")

    return {
        "resume_text": tailored,
        "pdf_path": pdf_path
    }