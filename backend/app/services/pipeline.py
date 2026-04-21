import re
from datetime import datetime, timezone
from hashlib import sha256

from app.services.matcher import score_job
from app.services.resume_ai import load_profile, generate_tailored_resume
from app.services.pdf_generator import save_resume_pdf
from app.services.job_parser import parse_job
from app.db.database import SessionLocal
from app.models.job import Job


def build_resume_filename(parsed):
    raw_name = f"{parsed['company']}_{parsed['title']}"
    sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", raw_name).strip("_")
    return sanitized[:80] or "resume_output"


def build_job_fingerprint(parsed):
    normalized_description = re.sub(r"\s+", " ", parsed["description"]).strip().lower()
    normalized_title = parsed["title"].strip().lower()
    normalized_company = parsed["company"].strip().lower()
    fingerprint_input = f"{normalized_company}|{normalized_title}|{normalized_description}"
    return sha256(fingerprint_input.encode("utf-8")).hexdigest()


def process_job(job_description, source="MANUAL"):

    # STEP 1 — PARSE
    parsed = parse_job(job_description)
    fingerprint = build_job_fingerprint(parsed)

    # STEP 2 — SCORE (use cleaned description)
    result = score_job(parsed["description"])

    score = result.get("final_score")  # use final_score
    decision = result.get("decision")
    job, is_duplicate = save_job_to_db(parsed, result, fingerprint, source)

    response = {
        "job_id": job.id,
        "score": score,
        "decision": decision,
        "source": job.source,
        "tracking_status": job.tracking_status,
        "times_seen": job.times_seen,
        "is_duplicate": is_duplicate,
        "resume_generated": False,
        "resume_path": job.resume_path,
    }

    # STEP 3 — RESUME GENERATION
    if decision in ["AUTO_APPLY", "REVIEW_AND_CUSTOMIZE"] and not job.resume_path:
        profile = load_profile()
        tailored = generate_tailored_resume(parsed["description"], profile)

        filename = build_resume_filename(parsed)
        path = save_resume_pdf(tailored, filename)

        db = SessionLocal()
        persisted_job = db.query(Job).filter(Job.id == job.id).first()
        persisted_job.resume_path = path
        persisted_job.tracking_status = "RESUME_GENERATED"
        persisted_job.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(persisted_job)
        db.close()

        response["resume_generated"] = True
        response["resume_path"] = path
        response["tracking_status"] = persisted_job.tracking_status

    elif job.resume_path:
        response["tracking_status"] = job.tracking_status

    return response


def save_job_to_db(parsed, result, fingerprint, source):
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    existing_job = db.query(Job).filter(Job.fingerprint == fingerprint).first()

    if existing_job:
        existing_job.title = parsed["title"]
        existing_job.company = parsed["company"]
        existing_job.description = parsed["description"]
        existing_job.semantic_score = result.get("semantic_score")
        existing_job.constraint_score = result.get("constraint_score")
        existing_job.final_score = result.get("final_score")
        existing_job.decision = result.get("decision")
        existing_job.source = source
        existing_job.times_seen = (existing_job.times_seen or 0) + 1
        existing_job.last_seen_at = now
        existing_job.updated_at = now

        if not existing_job.tracking_status or existing_job.tracking_status == "NEW":
            existing_job.tracking_status = "DUPLICATE_SKIPPED"

        db.commit()
        db.refresh(existing_job)
        db.close()
        return existing_job, True

    job = Job(
        title=parsed["title"],
        company=parsed["company"],
        description=parsed["description"],
        fingerprint=fingerprint,
        source=source,
        tracking_status="PROCESSED",
        times_seen=1,
        created_at=now,
        updated_at=now,
        last_seen_at=now,
        semantic_score=result.get("semantic_score"),
        constraint_score=result.get("constraint_score"),
        final_score=result.get("final_score"),
        decision=result.get("decision"),
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    db.close()

    return job, False
