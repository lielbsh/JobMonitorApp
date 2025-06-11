from sqlalchemy import func
from db.database import SessionLocal
from models import Job, Email
from datetime import timedelta, datetime
from schemas import JobData, MessageData

def email_exist(gmail_id: str) -> (Email | None):
    with SessionLocal() as db:
        existing = db.query(Email).filter_by(gmail_id=gmail_id).first()
        if existing: print(f"[{existing.id}] Email exist")
        return existing
    

def insert_email(message_data: MessageData, job_id: int) -> bool:
    with SessionLocal() as db:
        existing = db.query(Email).filter_by(gmail_id=message_data.gmail_id).first()
        if existing:
            return False

        email = message_data.to_email_model(job_id)
        db.add(email)
        db.commit()
        return True  


def insert_job(session, job_data: JobData) -> int:
    new_job = job_data.to_job_model()
    session.add(new_job)
    session.commit()
    session.refresh(new_job)
    print("New job saved to db, job Id =", new_job.id)
    return new_job.id


def update_job(session, job: Job, new_job: Job):
    updated = False

    if new_job.last_update > job.last_update:
        job.status = new_job.status
        job.last_update = new_job.last_update
        updated = True
        print(f"[{job.id}] Job Updated")
    
    for field in ['role', 'location', 'link']:
        if not getattr(job, field) and getattr(new_job, field):
            setattr(job, field, getattr(new_job, field))
            updated = True
            print(f"[{job.id}] Filled missing field: {field}")

    if updated:
        session.commit()
    return job.id


def update_or_create_job(job_data: JobData, email_data: MessageData):
    with SessionLocal() as db:
        company = job_data.company.lower() if job_data.company else None
        role = job_data.role.lower() if job_data.role else None
        thread_id = email_data.thread_id
        from_email = email_data.from_email

        if not company:
            print("Missing Company -> job didn't save to db")
            return

        if role:
            db_job = (
                db.query(Job)
                .filter(
                    func.lower(Job.company) == company,
                    func.lower(Job.role) == role,
                )
                .first()
            )
        else:
            jobs = (
                db.query(Job)
                .filter(func.lower(Job.company) == company)
                .all()
            )
            if len(jobs) == 1:
                db_job = jobs[0]
            else:
                db_job = next((j for j in jobs if j.thread_id == thread_id), None)
        
        if db_job:
            return update_job(db, db_job, job_data)
        
        return insert_job(db, job_data)
    
