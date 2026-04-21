# Job Automation

AI-assisted job processing project with a FastAPI backend, a Streamlit dashboard, SQLite job tracking, resume generation, and duplicate detection.

## What This Project Does

- Accepts a job description manually through the Streamlit UI or API
- Parses the role, company, skills, and raw description
- Scores the job against your profile in `backend/data/profile.json`
- Classifies the job as:
  - `AUTO_APPLY`
  - `REVIEW_AND_CUSTOMIZE`
  - `IGNORE`
- Generates a tailored resume PDF for strong matches
- Stores jobs in one shared SQLite database: `backend/jobs.db`
- Deduplicates repeated job submissions using a fingerprint of company, title, and description
- Tracks job lifecycle fields such as `times_seen`, `tracking_status`, `source`, and timestamps

## Project Structure

```text
job-automation/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── jobs.py
│   │   │   ├── pipeline.py
│   │   │   └── resume.py
│   │   ├── db/
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── application.py
│   │   │   ├── job.py
│   │   │   └── profile.py
│   │   ├── services/
│   │   │   ├── gmail_reader.py
│   │   │   ├── job_parser.py
│   │   │   ├── matcher.py
│   │   │   ├── pdf_generator.py
│   │   │   ├── pipeline.py
│   │   │   ├── resume_ai.py
│   │   │   ├── skill_extraction.py
│   │   │   └── skill_ontology.py
│   │   └── main.py
│   ├── data/
│   │   ├── generated_resumes/
│   │   └── profile.json
│   └── jobs.db
└── frontend/
    └── streamlit_app.py
```

## Core Flow

1. User submits a job description.
2. `job_parser.py` extracts title, company, and simple skills.
3. `matcher.py` scores the job against `profile.json`.
4. `pipeline.py` creates a fingerprint and checks for duplicates.
5. If the job is new and worth pursuing, `resume_ai.py` generates resume text.
6. `pdf_generator.py` saves the tailored resume under `backend/data/generated_resumes/`.
7. The job is stored in `backend/jobs.db`.
8. The Streamlit dashboard reads `/jobs` from the backend and displays tracked jobs.

## Deduplication And Tracking

The project now supports built-in deduplication and job tracking.

Each job stores:

- `fingerprint`: stable hash built from company, title, and description
- `source`: where the job came from, such as `MANUAL`
- `tracking_status`: current lifecycle state
- `resume_path`: generated resume file path if available
- `times_seen`: how many times the same job has been encountered
- `created_at`
- `updated_at`
- `last_seen_at`

Duplicate behavior:

- If a job is processed for the first time, a new row is created.
- If the same job is processed again, the existing row is updated.
- `times_seen` is incremented.
- Existing resume files are reused instead of generating duplicates.

## Requirements

Recommended Python version:

- Python 3.13+

Main libraries used by the project:

- `fastapi`
- `uvicorn`
- `streamlit`
- `sqlalchemy`
- `openai`
- `python-dotenv`
- `fpdf`
- `numpy`
- `sentence-transformers`
- `spacy`
- `pandas`
- `requests`
- `google-api-python-client`
- `google-auth`

If you do not already have dependencies installed, install them with:

```bash
pip install fastapi uvicorn streamlit sqlalchemy openai python-dotenv fpdf numpy sentence-transformers spacy pandas requests google-api-python-client google-auth
python -m spacy download en_core_web_sm
```

## Environment Setup

Create or update:

- `backend/.env`

Add:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Profile Configuration

Edit:

- [backend/data/profile.json](https://github.com/gallayagnesh/Job_Automation_AI_Project/blob/main/backend/data/profile.json)

Example shape:

```json
{
  "roles": ["AI Engineer", "ML Engineer"],
  "skills": ["Python", "AWS", "SQL", "NLP"],
  "experience_years": 2.3,
  "preferred_domains": ["AI", "FinTech", "Cloud"]
}
```

This file is the source of truth for:

- scoring jobs
- resume generation context
- skill matching

## Run The Backend

From the project root:

```bash
cd backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend routes:

- `GET /jobs`
- `POST /process-job`
- `POST /generate-resume`

## Run The Frontend

From the project root:

```bash
streamlit run frontend/streamlit_app.py
```

The dashboard expects the backend at:

```text
http://127.0.0.1:8000
```

## API Examples

### Process A Job

```bash
curl -X POST "http://127.0.0.1:8000/process-job?job_description=Senior%20Python%20AI%20Engineer%20at%20Example%20Corp.%20Must%20have%20Python,%20AWS,%20SQL,%20NLP.&source=MANUAL"
```

Example response:

```json
{
  "job_id": 10,
  "score": 0.783,
  "decision": "AUTO_APPLY",
  "source": "MANUAL",
  "tracking_status": "RESUME_GENERATED",
  "times_seen": 1,
  "is_duplicate": false,
  "resume_generated": true,
  "resume_path": "/absolute/path/to/backend/data/generated_resumes/example.pdf"
}
```

### Fetch Stored Jobs

```bash
curl "http://127.0.0.1:8000/jobs"
```

### Generate Resume Only

```bash
curl -X POST "http://127.0.0.1:8000/generate-resume?job_description=Machine%20Learning%20Engineer%20with%20Python%20and%20AWS"
```

## Gmail Reader

There is an early Gmail integration in:

- [backend/app/services/gmail_reader.py](https://github.com/gallayagnesh/Job_Automation_AI_Project/blob/main/backend/app/services/gmail_reader.py)

It currently:

- reads Gmail messages matching a jobs-related subject query
- decodes message bodies
- returns raw job-like email content

It expects:

- `token.json` to exist and be valid for Gmail API access

Notes:

- Gmail ingestion is not yet fully connected into the tracking pipeline by default
- if you wire it into the pipeline, pass `source="GMAIL"` to `process_job(...)`

## Offline And Fallback Behavior

The project includes a few safety fallbacks:

- If `sentence-transformers` cannot load the embedding model locally, job scoring falls back to keyword overlap.
- If OpenAI resume generation fails, a local fallback resume template is returned.
- SQLite schema upgrades are applied automatically on startup for the `jobs` table.

## Database

Single active database file:

- [backend/jobs.db](/Users/yagnesh/Mine/Projects/job-automation/backend/jobs.db)

The frontend and backend both use this file.

## Common Issues

### 1. No Jobs Showing In Streamlit

Make sure:

- backend is running on port `8000`
- Streamlit is pointed to `http://127.0.0.1:8000`
- jobs are being written into `backend/jobs.db`

### 2. OpenAI Resume Generation Fails

Check:

- `OPENAI_API_KEY` is set in `backend/.env`

The project will still return a fallback resume if the API call fails.

### 3. Sentence Transformer Model Is Not Available

If the embedding model is not cached locally, matching will fall back to keyword overlap scoring instead of crashing the app.

### 4. Gmail Reader Does Not Work

Check:

- `token.json` exists
- Gmail API credentials are valid
- the installed Google client libraries are present

## Current Limitations

- Gmail ingestion is not yet fully automated into the main pipeline
- job parsing is still heuristic-based and fairly simple
- there is no full authentication or user management
- existing historical duplicates are not automatically merged into one row
- the dashboard is functional but still minimal

## Next Good Improvements

- connect Gmail ingestion directly into `process_job(...)`
- add a `POST /jobs/{id}/status` endpoint for manual status changes
- track application events in the `applications` table
- improve parsing with cleaner extraction for company, title, and links
- add export options for shortlisted jobs
- add tests for deduplication and scoring

## License

Use this project however you want for personal learning or portfolio work unless you want to add a formal license later.
