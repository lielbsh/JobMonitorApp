import re
from schemas import JobData

import logging
logger = logging.getLogger(__name__)

def extract_linkedin_application_data(body: str, last_update) -> JobData | None:
    lines = body.strip().splitlines()
    company = role = link = None
    
    role = lines[1].strip()
    company = lines[2].strip()
    location = lines[3].strip()
    link_match = re.search(r"https://www\.linkedin\.com/comm/jobs/view/\S+", lines[4])
    link = link_match.group(0).strip() if link_match else None

    if not company:
        company_match = re.search(r"Your application was sent to (.+)", lines[0])
        company = company_match.group(1).strip() if company_match else None
    
    return JobData(
        source="linkedin",
        status="Submitted Application",
        company=company,
        role=role,
        link=link,
        location=location,
        last_update=last_update
    )
    
def extract_linkedin_rejection_data(subject: str, body: str, last_update):
    if "email_jobs_application_rejected" not in body:
        return None

    match = re.search(r"Your application to (.+?) at (.+)", subject)
    if match:
        role, company = match.group(1).strip(), match.group(2).strip()
        return JobData(
                source="linkedin",
                status="Rejected",
                company=company,
                role=role,
                link=None,
                location=None,
                last_update=last_update
            )
    return None


def process_linkedin_message(subject: str, body: str, last_update) -> JobData | None:
    try:
        if "your application to" in subject.lower():
            return extract_linkedin_rejection_data(subject, body, last_update)
        elif "your application was sent to" in body.lower():
            return extract_linkedin_application_data(body, last_update)
        return None
    
    except Exception as e:
            logger.warning(f"⚠️ Error in LinkedIn parser: {e}")
            return None