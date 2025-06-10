from sqlalchemy import func
from db.database import SessionLocal
from models import Job, Email


def insert_job(session, job_data: dict[str, any]) -> int:
    new_job = Job(
        company=job_data.get("company"),
        role=job_data.get("role"),
        status=job_data.get("status"),
        source=job_data.get("source"),
        last_update=job_data.get("last_update"),
        location=job_data.get("location"),
        link=job_data.get("link"),
    )
    session.add(new_job)
    session.commit()
    session.refresh(new_job)
    return new_job.id


def insert_email(gmail_id: str, thread_id: str, msg_info: dict, job_id: int):
    with SessionLocal() as db:
        existing = db.query(Email).filter_by(gmail_id=gmail_id).first()
        if existing:
            return

        email = Email(
            gmail_id=gmail_id,
            thread_id=thread_id,
            job_id=job_id,
            subject=msg_info.get("subject"),
            body=msg_info.get("body"),
            from_email=msg_info.get("from"),
            date=msg_info.get("date"),
        )
        db.add(email)
        db.commit()


def update_or_create_job(job_data: dict[str, any]):
    with SessionLocal() as db:
        company = job_data.get("company" or "").lower()
        role = job_data.get("role" or "").lower()

        if company and role:
            job = (
                db.query(Job)
                .filter(
                    func.lower(Job.company) == company,
                    func.lower(Job.role) == role,
                )
                .first()
            )
        elif company:
            jobs = (
                db.query(Job)
                .filter(func.lower(Job.company) == company)
                .all()
            )
            if len(jobs) == 1:
                job = jobs[0]
            else:
                job = None
        else:
            job = None

        if job:
            if job.status != job_data.get("status"):
                job.status = job_data.get("status")
                job.last_update = job_data.get("last_update")
                db.commit()
            return job.id

        return insert_job(db, job_data)
