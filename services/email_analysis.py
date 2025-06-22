from schemas import JobData, MessageData
from services.openai_client import call_openaiapi, create_prompt
from services.regex_extraction import process_linkedin_message


def get_job_data_from_email(msg_data: MessageData) -> JobData | None:
    """
    Extract job data from an email message.
    If the email is from LinkedIn and contains a confirmation/rejection message, it will extract the job data. Otherwise, it will use OpenAI API to analyze the email content.
    If the OpenAI API call fails, it will return None.
    """
    is_linkedin = "linkedin.com" in msg_data.from_email.lower()
    last_update = msg_data.date

    if is_linkedin:
        job = process_linkedin_message(msg_data.subject, msg_data.body, last_update)
        if job:
            return job
    
    prompt = create_prompt(msg_data)
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


def print_job_details(job_data: JobData):
    print(f"Source   : {job_data.source}")
    print(f"Status   : {job_data.status}")
    print(f"Company  : {job_data.company}")
    print(f"Role     : {job_data.role}")
    print(f"Location : {job_data.location}")
    print(f"Link     : {job_data.link}")