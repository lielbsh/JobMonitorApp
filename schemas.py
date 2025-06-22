from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class JobData:
    source: str
    status: str
    company: Optional[str] = None
    role: Optional[str] = None
    link: Optional[str] = None
    location: Optional[str] = None
    last_update: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if self.company is not None:
            self.company = self.company.strip().lower()

        if self.role:
            self.role = self.role.strip().lower()

    def to_dict(self):
        return asdict(self)


@dataclass
class MessageData:
    from_email: str
    subject: str
    date: datetime
    body: Optional[str] = None
    gmail_id: Optional[str] = None
    thread_id: Optional[str] = None

    def to_dict(self):
        return asdict(self)
