from fastapi import APIRouter
from app.db.database import SessionLocal
from app.models.job import Job

router = APIRouter()


def serialize_job(job):
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "link": job.link,
        "fingerprint": job.fingerprint,
        "source": job.source,
        "resume_path": job.resume_path,
        "tracking_status": job.tracking_status,
        "times_seen": job.times_seen,
        "semantic_score": job.semantic_score,
        "constraint_score": job.constraint_score,
        "final_score": job.final_score,
        "decision": job.decision,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "last_seen_at": job.last_seen_at.isoformat() if job.last_seen_at else None,
    }


@router.get("/jobs")
def get_jobs():
    db = SessionLocal()
    jobs = db.query(Job).order_by(Job.last_seen_at.desc(), Job.id.desc()).all()
    db.close()

    return [serialize_job(job) for job in jobs]
