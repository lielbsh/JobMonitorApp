from sqlalchemy import or_, and_
from db.database import SessionLocal
from db.models import Job, Email
from datetime import timedelta, datetime
import logging
logger = logging.getLogger(__name__)

def email_exist(gmail_id: str) -> (Email | None):
    with SessionLocal() as db:
        existing = db.query(Email).filter_by(gmail_id=gmail_id).first()
        if existing: 
            logger.info(f"Email already exists in db, id={existing.id}, subject={existing.subject}")
        return existing
    

def insert_email(message_data: dict, job_id: int) -> bool:
    with SessionLocal() as db:
        existing = db.query(Email).filter_by(gmail_id=message_data.get("gmail_id")).first()
        if existing:
            return False

        email = Email(**message_data, job_id=job_id)
        db.add(email)
        db.commit()
        return True  


def insert_job(session, job_data: dict) -> int | None:
    if job_data.get("status") == "Not Relevant" or not job_data.get("company"):
        return None
    new_job = Job(**job_data)
    session.add(new_job)
    session.commit()
    session.refresh(new_job)
    logger.info(f"New job saved to db, id={new_job.id}")
    return new_job.id


def update_job(session, job: Job, new_job: dict) -> int:
    updated = False

    if new_job.get("last_update") > job.last_update:
        job.status = new_job.get("status")
        job.last_update = new_job.get("last_update")
        updated = True
        logger.info(f"Job Updated, id={job.id}")
    
    for field in ['role', 'location', 'link']:
        if (new_job_value := new_job.get(field)) and not getattr(job, field, None):
            setattr(job, field, new_job_value)
            updated = True
            logger.info(f"Filled missing field: {field}, id={job.id}")

    if updated:
        session.commit()
    return job.id


def update_or_create_job(job_data: dict, email_data: dict):
    with SessionLocal() as db:
        company = job_data.get("company", None)
        company = company.lower() if company else None
        role = job_data.get("role", None)
        role = role.lower() if role else None
        thread_id = email_data.get("thread_id")
        from_email = email_data.get("from_email")

        if not company:
            logger.warning("Missing Company -> job didn't save to db")
            return
        
        one_month_ago = datetime.now() - timedelta(days=30)
        db_job = None

        if role:
            db_job = (
                db.query(Job)
                .filter(
                    Job.company == company,
                    Job.role == role,
                    Job.last_update >= one_month_ago,
                )
                .order_by(Job.created_at.desc())
                .first()
            )
            if not db_job:
                jobs = (
                    db.query(Job)
                    .filter(
                        Job.company.startswith(company),
                        Job.role.startswith(role),
                        Job.last_update >= one_month_ago,
                    )
                    .order_by(Job.created_at.desc())
                    .first()
                )
        if not db_job:
            jobs = (
                db.query(Job)
                .filter(
                    Job.company.startswith(company),
                    Job.last_update >= one_month_ago,
                )
                .order_by(Job.created_at.desc())
                .limit(2).all()
            )
            if len(jobs) == 1:
                db_job = jobs[0]
            elif len(jobs) > 1:
                db_job = (
                    db.query(Job).join(Email)
                    .filter(
                        or_(
                            Email.thread_id == thread_id,
                            and_(
                                Email.from_email == from_email,
                                ~Email.from_email.ilike('%linkedin.com%')
                            )
                        )
                    )
                    .first()
                )
        
        if db_job:
            return update_job(db, db_job, job_data)
        
        return insert_job(db, job_data)