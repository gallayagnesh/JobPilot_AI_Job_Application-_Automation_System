import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_master_resume(path="data/master_resume.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def generate_tailored_resume(job_description, master_resume):

    prompt = f"""
You are an expert ATS resume optimizer.

TASK:
Rewrite the resume to match the job description.

RULES:
- Do NOT invent fake experience
- Reorder bullet points for relevance
- Emphasize matching skills
- Optimize keywords for ATS
- Keep concise professional tone

JOB DESCRIPTION:
{job_description}

MASTER RESUME:
{master_resume}

OUTPUT FORMAT:

NAME
SUMMARY

SKILLS

EXPERIENCE

PROJECTS

EDUCATION
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content