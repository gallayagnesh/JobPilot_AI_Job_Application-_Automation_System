# Canonical mapping (expand over time)

SKILL_MAP = {
    "python": ["python"],
    "sql": ["sql", "postgresql", "mysql", "sqlite"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "opencv"],
    "deep learning": ["tensorflow", "pytorch", "keras", "cnn", "rnn"],
    "machine learning": ["machine learning", "sklearn", "xgboost", "random forest"],
    "aws": ["aws", "ec2", "s3", "lambda", "cloudwatch"],
    "gcp": ["gcp", "bigquery", "cloud functions", "pubsub"],
    "data analysis": ["pandas", "numpy", "excel"],
    "backend": ["backend", "flask", "fastapi", "django"],
    "apis": ["apis", "api", "rest api", "graphql"]
}

def normalize_skills(text):
    text = text.lower()
    normalized = set()

    for canonical, variants in SKILL_MAP.items():
        if canonical in text:
            normalized.add(canonical)

        for v in variants:
            if v in text:
                normalized.add(canonical)

    return list(normalized)
