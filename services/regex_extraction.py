import re
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