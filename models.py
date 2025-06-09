from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String)
    role = Column(String)
    status = Column(String)
    source = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    last_update = Column(DateTime)
    location = Column(String)
    link = Column(String)

    emails = relationship("Email", back_populates="job", cascade="all, delete")

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    subject = Column(String)
    body = Column(Text)
    from_email = Column(String)
    date = Column(DateTime)
    gmail_id = Column(String, unique=True)
    thread_id = Column(String)

    job = relationship("Job", back_populates="emails")
