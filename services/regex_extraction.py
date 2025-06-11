import re
from config import APPLICATION_KEYWORDS, EXTRACTION_PATTERNS, ROLE_PATTERNS
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
        search_in_patterns(msg_lower ,patterns)
        if search_in_patterns(msg_lower, patterns):
            return label
    return None

def search_in_patterns(text:str ,patterns:list[str]):
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group().strip()
    return None

def extract_company_and_role(sender, subject, body):
    text = f"Subject: {subject} \nBody: {body}"
    company, role = None, None

    for pattern, kind in EXTRACTION_PATTERNS:
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

    if not role:
        role = search_in_patterns(text, ROLE_PATTERNS)

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
