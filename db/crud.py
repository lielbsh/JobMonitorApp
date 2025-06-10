from sqlalchemy import func
from db.database import SessionLocal
from models import Job, Email
from datetime import timedelta, datetime
from schemas import JobData, MessageData


def insert_job(session, job_data: JobData) -> int:
    new_job = job_data.to_job_model()
    session.add(new_job)
    session.commit()
    session.refresh(new_job)
    return new_job.id


def insert_email(message_data: MessageData, job_id: int) -> bool:
    with SessionLocal() as db:
        existing = db.query(Email).filter_by(gmail_id=message_data.gmail_id).first()
        if existing:
            return False

        email = message_data.to_email_model(job_id)
        db.add(email)
        db.commit()
        return True


def update_or_create_job(job_data: JobData, email_data: MessageData):
    with SessionLocal() as db:
        company = job_data.company.lower() if job_data.company else None
        role = job_data.role.lower() if job_data.role else None


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
            if job.status != job_data.status:
                job.status = job_data.status
                job.last_update = job_data.last_update
                db.commit()
            return job.id
        
        return insert_job(db, job_data)
        


