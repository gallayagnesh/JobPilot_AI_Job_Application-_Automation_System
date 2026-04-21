import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_gmail_service():
    creds = Credentials.from_authorized_user_file("token.json")
    return build("gmail", "v1", credentials=creds)


def get_job_emails():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="subject:(jobs OR hiring OR opportunity)"
    ).execute()

    messages = results.get("messages", [])

    jobs = []

    for msg in messages[:5]:
        data = service.users().messages().get(userId="me", id=msg["id"]).execute()

        payload = data["payload"]["body"].get("data", "")
        decoded = base64.urlsafe_b64decode(payload).decode("utf-8")

        jobs.append(decoded)

    return jobs