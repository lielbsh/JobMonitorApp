import re
from config import APPLICATION_KEYWORDS
from schemas import MessageData, JobData


def extract_from_linkedin_confirmation(body: str, last_update) -> JobData | None:
    lines = body.strip().splitlines()
    company = role = link = None
    status = "Submitted Application"
    source = "linkedin"
    
    try:
        role = lines[1].strip()
        company = lines[2].strip()
        location = lines[3].strip()
        link_match = re.search(r"https://www\.linkedin\.com/comm/jobs/view/\S+", lines[4])
        link = link_match.group(0).strip() if link_match else None

        if not company:
            company_match = re.search(r"Your application was sent to (.+)", lines[0])
            company = company_match.group(1).strip() if company_match else None
        
        return JobData(
            source=source,
            status=status,
            company=company,
            role=role,
            link=link,
            location=location,
            last_update=last_update
        )

    except Exception as e:
            print(f"⚠️ Error in LinkedIn parser: {e}")
            return None
    

def classify_message(subject: str, body: str):
    """
    Classifies the message (status) based on keyword presence in subject and body.
    """
    msg_lower = f"{subject}\n{body}".lower()
    for label, patterns in APPLICATION_KEYWORDS.items():
        for pattern in patterns:
            if re.search(pattern, msg_lower):
                return label
    return None


def extract_company_and_role(sender, subject, body):
    text = f"Subject: {subject} \nBody: {body}"
    company, role = None, None

    patterns = [
        (r"application for (.+?) at ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "role_company"),
        (r"for the ([A-Za-z0-9\- &_]+) role at ([A-Z][a-zA-Z0-9&.\-']+?)(?=[\s\.,]|$)", "role_company"),
        (r"for the ([A-Za-z0-9\- &_]+) position at ([A-Z][a-zA-Z& .\-']+?)(?=[\s\.,]|$)", "role_company"),
        (r"sent to ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "company"),
        (r"thanks for applying to ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "company"),
        (r"Thank you for applying to ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "company"),
        (r"has been received by ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "company"),
        (r"\b([A-Z][\w&.\-']{1,50})\s+(HR Team|Recruiting Team|HR)\b", "company"),
        (r"\b([A-Z][\w&.\-']{1,50})'s\s+(Talent Team|HR Team|Recruiting Team)\b", "company"),
        (r"for the role of ([A-Za-z0-9\- &_]{2,})", "role"),
        (r"for the ([A-Za-z0-9&\-.,' ]+?) position", "role"),
        (r"position of ([A-Za-z0-9\- &_]{2,})", "role"),
        (r"application for ([A-Z][a-zA-Z0-9\- &]+)(?:\s*-\s*\d+)?", "role"),
    ]

    for pattern, kind in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            if kind == "role_company":
                role = match.group(1).strip()
                company = match.group(2).strip()
            elif kind == "company":
                company = match.group(1).strip()
            elif kind == "role":
                role = match.group(1).strip()
            break

    role_patterns = [
        r"\b(?:[Ss]enior|[Jj]unior)?\s*(?:[Dd]eveloper|[Dd]ata|[Ss]oftware|[Pp]roduct|[Mm]arketing|[Ss]ales|[Ee]ngineering|[Hh]R|[Oo]perations|[Ff]ull[- ]?[Ss]tack|[Ss]upport|[Ss]olution)\s+\w+(?:\s+\w+)?",
        r"\b(?:Backend Engineer|Frontend Engineer|Site Reliability Engineer I|Technical Solution Engineer)\b"
    ]

    def search_in_patterns(text:str ,patterns:list[str]):
        for line in text.splitlines():
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group().strip()
        return None

    if not role:
        role = search_in_patterns(text, role_patterns)

    return company, role


def try_extract_with_rules(msg_data: MessageData) -> JobData | None:
    status = classify_message(msg_data.subject, msg_data.body)
    if not status: return
    company, role = extract_company_and_role(msg_data.from_email, msg_data.subject, msg_data.body)
    if not company or not role: return

    return JobData(
            source='regex',
            status=status,
            company=company,
            role=role,
            link=None,
            location=None,
            last_update=msg_data.date
        )
