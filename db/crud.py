from locale import normalize
from db.database import SessionLocal
from models import Job, Email

def insert_job(job_data: dict[str, any]) -> int:
    db = SessionLocal()
    try:
        new_job = Job(
            company=job_data.get("company"),
            role=job_data.get("role"),
            status=job_data.get("status"),
            source=job_data.get("source"),
            last_update=job_data.get("last_update"),
            location = job_data.get("location"),
            link = job_data.get("link"),
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return new_job.id
    finally:
        db.close()

def insert_email(gmail_id: str, thread_id: str, msg_info: dict, job_id: int):
    db = SessionLocal()
    existing = db.query(Email).filter_by(gmail_id=gmail_id).first()
    if existing:
        db.close()
        return

    email = Email(
        gmail_id = gmail_id,
        thread_id = thread_id,
        job_id = job_id,
        subject = msg_info.get("subject"),
        body = msg_info.get("body"),
        from_email = msg_info.get("from"),
        date = msg_info.get("date")
    )
    db.add(email)
    db.commit()
    db.close()
