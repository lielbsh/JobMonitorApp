import logging
import os
import json
import openai
from schemas import MessageData
from settings import OPENAI_API_KEY

import logging
logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key=OPENAI_API_KEY)


def call_openaiapi(prompt: str) -> json:
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
        result = response.choices[0].message.content
        try:
            parsed = json.loads(result)
            return {
                "status": "success",
                "data": parsed
            }
        except json.JSONDecodeError:
            logger.error("⚠️ Model response is not valid JSON.")
            return {
                "status": "error",
                "message": "Model response is not valid JSON.",
                "raw_output": result
            }
    
    except openai.AuthenticationError:
        logger.error("⚠️ Authentication failed: Please check your API key.")
        return {
            "status": "error",
            "message": "Authentication failed. Please check your API key."
        }
        
    except Exception as e:
        logger.error("⚠️ Unexpected error:", e)
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def create_prompt(email_data: MessageData):
    prompt = f"""
    You are an assistant that extracts job application information from email messages.

    Given the following email:
    From: {email_data.from_email}
    Subject: {email_data.subject}
    Body: {email_data.body}

    Classify the email and return the following fields:
    - status: (string) One of ['Submitted Application', 'Rejected', 'Interview Process', 'Home Assignment', 'Accepted', 'Not Relevant'] 
    - company: The company name (string or null)
    - role: The job title or position (string or null)
    - link: A valid URL if one is included in the email (string or null)

    Return a raw JSON object with keys: status, company, role, link.
    Do NOT include explanations, extra text, or markdown formatting.
    """
    return prompt