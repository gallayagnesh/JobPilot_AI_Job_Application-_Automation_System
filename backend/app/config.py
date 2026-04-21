import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Matching thresholds
    AUTO_APPLY_THRESHOLD = 0.75
    REVIEW_THRESHOLD = 0.55

    # Model config
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"

settings = Settings()