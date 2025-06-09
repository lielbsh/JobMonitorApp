def analyze_email(msg_info):
    is_linkedin = "linkedin.com" in msg_info['from'].lower()
    link = None
    location = None
    last_update = msg_info.get("date")

    if is_linkedin and "your application was sent to" in msg_info['body'].lower():
        status, source, company, role, link, location = extract_from_linkedin_confirmation(msg_info['body'])
        return {
            "source": source,
            "status": status,
            "company": company,
            "role": role,
            "link": link,
            "location": location,
            "last_update": last_update
        }

    return

def print_analysis(idx, analysis, msg_info):
    print(f"\n[{idx}] 📧 EMAIL: {msg_info['subject']} | from {msg_info['from']}")
    print(f"Source   : {analysis.get('source')}")
    print(f"Status   : {analysis.get('status')}")
    print(f"Company  : {analysis.get('company')}")
    print(f"Role     : {analysis.get('role')}")
    print(f"Location : {analysis.get('location')}")
    print(f"Link     : {analysis.get('link')}")

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