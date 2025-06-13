# schemas.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from models import Job, Email 

@dataclass
class JobData:
    source: str
    status: str
    company: str
    role: Optional[str] = None
    link: Optional[str] = None
    location: Optional[str] = None
    last_update: datetime = field(default_factory=datetime.now)

    
    def __post_init__(self):
        if not self.company or not self.company.strip():
            raise ValueError("company is required")

        self.company = self.company.strip().lower()

        if self.role:
            self.role = self.role.strip().lower()


    def to_job_model(self) -> Job:
        return Job(
            source=self.source,
            status=self.status,
            company=self.company,
            role=self.role,
            link=self.link,
            location=self.location,
            last_update=self.last_update,
            created_at=self.created_at
        )

    @classmethod
    def from_job_model(cls, job: Job, **kwargs) -> 'JobData':
        return cls(
            company=job.company,
            role=job.role,
            status=job.status,
            source=job.source or "email",
            last_update=job.last_update or datetime.now(),
            created_at=job.created_at or datetime.now(),
            location=job.location,
            link=job.link,
            **kwargs
        )

@dataclass
class MessageData:
    from_email: str
    subject: str
    date: datetime
    body: Optional[str] = None
    gmail_id: Optional[str] = None
    thread_id: Optional[str] = None
    
    def to_email_model(self, job_id: int) -> Email:
        return Email(
            job_id=job_id,
            subject=self.subject,
            body=self.body,
            from_email=self.from_email,
            date=self.date,
            gmail_id=self.gmail_id,
            thread_id=self.thread_id
        )