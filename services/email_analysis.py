from schemas import JobData, MessageData
from services.openai_client import call_openaiapi, count_tokens, create_prompt
from services.regex_extraction import extract_from_linkedin_confirmation, try_extract_with_rules

def get_job_data_from_email(msg_data: MessageData) -> JobData | None:
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
    result_data = result["data"]

    return JobData(
        source="openai_api",
        status=result_data["status"],
        company=result_data["company"],
        role=result_data["role"],
        link=result_data["link"],
        location=None,
        last_update=last_update
    )


def print_job_details(idx: int, job_data: JobData, msg_info: MessageData):
    print(f"\n[{idx}] 📧 EMAIL: {msg_info.subject} | from {msg_info.from_email}")
    print(f"Source   : {job_data.source}")
    print(f"Status   : {job_data.status}")
    print(f"Company  : {job_data.company}")
    print(f"Role     : {job_data.role}")
    print(f"Location : {job_data.location}")
    print(f"Link     : {job_data.link}")