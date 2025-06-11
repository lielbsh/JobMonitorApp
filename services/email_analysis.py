from schemas import JobData, MessageData
from services.openai_client import call_openaiapi, count_tokens, create_prompt
from services.regex_extraction import extract_from_linkedin_confirmation, try_extract_with_rules

def analyze_email(msg_data: MessageData) -> JobData | None:
    is_linkedin = "linkedin.com" in msg_data.from_email.lower()
    last_update = msg_data.date

    if is_linkedin and "your application was sent to" in (msg_data.body or "").lower():
        job = extract_from_linkedin_confirmation(msg_data.body, last_update)
        if job:
            return job
    
    rule_result = try_extract_with_rules(msg_data)
    if rule_result:
        return rule_result

    prompt = create_prompt(msg_data)
    print("Number of tokens: ",count_tokens(prompt))
    result = call_openaiapi(prompt) 
    if result["status"] == "error":
        print(f"❌ OpenAI error: {result['message']}")
        return None

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