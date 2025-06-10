import re

from schemas import JobData, MessageData
from services.openai_client import call_openaiapi, count_tokens, create_prompt

def analyze_email(msg_data: MessageData) -> JobData:
    is_linkedin = "linkedin.com" in msg_data.from_email.lower()
    link = None
    location = None
    last_update = msg_data.date

    if is_linkedin and "your application was sent to" in (msg_data.body or "").lower():
        status, source, company, role, link, location = extract_from_linkedin_confirmation(msg_data.body)
        return JobData(
            source=source,
            status=status,
            company=company,
            role=role,
            link=link,
            location=location,
            last_update=last_update
        )

    prompt = create_prompt(msg_data)
    result = call_openaiapi(prompt) 
    print("Number of tokens: ",count_tokens(prompt))

    return JobData(
        source="openai_api",
        status=result["status"],
        company=result["company"],
        role=result["role"],
        link=result["link"],
        location=None,
        last_update=last_update
    )

def print_analysis(idx: int, analysis: JobData, msg_info: MessageData):
    print(f"\n[{idx}] 📧 EMAIL: {msg_info.subject} | from {msg_info.from_email}")
    print(f"Source   : {analysis.source}")
    print(f"Status   : {analysis.status}")
    print(f"Company  : {analysis.company}")
    print(f"Role     : {analysis.role}")
    print(f"Location : {analysis.location}")
    print(f"Link     : {analysis.link}")


def extract_from_linkedin_confirmation(body: str):
    lines = body.strip().splitlines()
    company = role = link = None
    status = "Submitted Application"
    source = "linkedin"
    
    # Try to extract company from the first line
    try:
        role = lines[1].strip()
        company = lines[2].strip()
        location = lines[3].strip()
        link_match = re.search(r"https://www\.linkedin\.com/comm/jobs/view/\S+", lines[4])
        link = link_match.group(0).strip() if link_match else None

        if not company:
            company_match = re.search(r"Your application was sent to (.+)", lines[0])
            company = company_match.group(1).strip() if company_match else None
        
        return status, source, company, role, link, location

    except Exception as e:
            print(f"⚠️ Error in LinkedIn parser: {e}")
            return None, None, None, None, None, None