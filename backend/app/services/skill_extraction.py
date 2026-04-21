import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

# keywords that indicate importance
STRONG_SIGNALS = ["must", "required", "mandatory", "need to"]
WEAK_SIGNALS = ["preferred", "good to have", "nice to have"]


def extract_skills(job_description):
    doc = nlp(job_description.lower())

    required_skills = []
    preferred_skills = []

    for sent in doc.sents:
        text = sent.text

        if any(word in text for word in STRONG_SIGNALS):
            required_skills.append(text)
        elif any(word in text for word in WEAK_SIGNALS):
            preferred_skills.append(text)

    return {
        "required": required_skills,
        "preferred": preferred_skills
    }
