import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_profile(path=None):
    profile_path = Path(path) if path else DATA_DIR / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


def profile_to_resume_context(profile):
    roles = ", ".join(profile.get("roles", [])) or "Not provided"
    skills = ", ".join(profile.get("skills", [])) or "Not provided"
    domains = ", ".join(profile.get("preferred_domains", [])) or "Not provided"
    experience = profile.get("experience_years", "Not provided")

    return (
        f"Target Roles: {roles}\n"
        f"Skills: {skills}\n"
        f"Preferred Domains: {domains}\n"
        f"Experience: {experience} years"
    )


def generate_fallback_resume(job_description, profile):
    roles = ", ".join(profile.get("roles", [])) or "Software Engineer"
    skills = profile.get("skills", [])
    domains = ", ".join(profile.get("preferred_domains", [])) or "Technology"
    experience = profile.get("experience_years", "N/A")
    highlighted_skills = ", ".join(skills[:8]) if skills else "Python, APIs, SQL"

    return f"""CANDIDATE NAME
SUMMARY
Engineer targeting {roles} opportunities with {experience} years of experience across {domains}. Background includes hands-on work with {highlighted_skills}. Interested in aligning past work to roles involving the responsibilities described in the job posting.

SKILLS
{", ".join(skills) if skills else "Python, SQL, APIs"}

EXPERIENCE
- Applied software and AI engineering skills to build practical backend and automation solutions.
- Worked with production-oriented tools and cloud platforms relevant to target roles.
- Adapted technical work to business needs while keeping implementation concise and maintainable.

PROJECTS
- Tailored resume generated from profile data for this job description:
{job_description[:500]}

EDUCATION
- Add your education details here.
"""


def generate_tailored_resume(job_description, profile=None):
    profile = profile or load_profile()
    profile_context = profile_to_resume_context(profile)

    prompt = f"""
You are an expert ATS resume optimizer.

TASK:
Generate a tailored resume using the candidate profile and the job description.

RULES:
- Do NOT invent fake experience
- Reorder strengths for relevance
- Emphasize matching skills from the profile
- Optimize keywords for ATS
- Keep concise professional tone
- If a detail is missing, leave it generic instead of fabricating it

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{profile_context}

OUTPUT FORMAT:

NAME
SUMMARY

SKILLS

EXPERIENCE

PROJECTS

EDUCATION
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception:
        return generate_fallback_resume(job_description, profile)
