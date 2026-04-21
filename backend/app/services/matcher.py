import json
from pathlib import Path
from functools import lru_cache

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

from app.services.skill_extraction import extract_skills
from app.services.skill_ontology import normalize_skills
from app.config import settings

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@lru_cache(maxsize=1)
def get_model():
    if SentenceTransformer is None:
        return None

    try:
        return SentenceTransformer(settings.EMBEDDING_MODEL, local_files_only=True)
    except Exception:
        return None


def load_profile(path=None):
    profile_path = Path(path) if path else DATA_DIR / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


def profile_to_text(profile):
    return (
        "Roles: " + ", ".join(profile["roles"]) + "\n" +
        "Skills: " + ", ".join(profile["skills"]) + "\n" +
        "Domains: " + ", ".join(profile["preferred_domains"]) + "\n" +
        f"Experience: {profile['experience_years']} years"
    )


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def keyword_overlap_score(profile, job_description):
    profile_terms = {
        skill.lower().strip()
        for skill in profile.get("skills", []) + profile.get("roles", []) + profile.get("preferred_domains", [])
    }
    job_text = job_description.lower()
    matches = [term for term in profile_terms if term and term in job_text]

    if not profile_terms:
        return 0.0

    return len(matches) / len(profile_terms)


def score_job(job_description):

    profile = load_profile()
    profile_text = profile_to_text(profile)
    model = get_model()

    if model is not None:
        emb_profile = model.encode(profile_text)
        emb_job = model.encode(job_description)
        semantic_score = float(cosine_similarity(emb_profile, emb_job))
    else:
        semantic_score = keyword_overlap_score(profile, job_description)

    # NEW: hard constraint score
    constraint_score = check_required_skills(job_description, profile)

    # combine both
    final_score = (0.7 * semantic_score) + (0.3 * constraint_score)

    # HARD FILTER (important)
    if constraint_score < 0.4:
        decision = "IGNORE"
    elif final_score >= settings.AUTO_APPLY_THRESHOLD:
        decision = "AUTO_APPLY"
    elif final_score >= settings.REVIEW_THRESHOLD:
        decision = "REVIEW_AND_CUSTOMIZE"
    else:
        decision = "IGNORE"

    return {
        "semantic_score": round(semantic_score, 3),
        "constraint_score": round(constraint_score, 3),
        "final_score": round(final_score, 3),
        "decision": decision
    }

def check_required_skills(job_description, profile):

    extracted = extract_skills(job_description)
    required_blocks = extracted["required"]

    profile_skills = get_normalized_profile_skills(profile)

    matched = 0
    total = len(required_blocks)

    for block in required_blocks:
        normalized_block = normalize_skills(block)

        if any(skill in profile_skills for skill in normalized_block):
            matched += 1

    if total == 0:
        return 1.0

    return matched / total

def get_normalized_profile_skills(profile):
    base_skills = [s.lower() for s in profile["skills"]]

    normalized = set(base_skills)

    for skill in base_skills:
        normalized.update(normalize_skills(skill))

    return list(normalized)
