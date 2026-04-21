import re


def extract_title(text):
    lines = text.split("\n")
    for line in lines[:5]:
        if len(line) < 80:
            return line.strip()
    return "Unknown"


def extract_company(text):
    patterns = [
        r"at\s+([A-Z][a-zA-Z0-9& ]+)",
        r"Company:\s*(.*)"
    ]

    for p in patterns:
        match = re.search(p, text)
        if match:
            return match.group(1).strip()

    return "Unknown"


def extract_skills(text):
    skill_keywords = [
        "python", "aws", "gcp", "tensorflow",
        "pytorch", "sql", "flask", "ml", "data"
    ]

    found = []

    text_lower = text.lower()

    for skill in skill_keywords:
        if skill in text_lower:
            found.append(skill)

    return list(set(found))


def parse_job(text):

    return {
        "title": extract_title(text),
        "company": extract_company(text),
        "skills": extract_skills(text),
        "description": text
    }