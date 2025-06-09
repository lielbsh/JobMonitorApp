import os
import json
import openai
import tiktoken
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

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
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Model response is not valid JSON.",
                "raw_output": result
            }
    
    except openai.AuthenticationError:
        print("⚠️ Authentication failed: Please check your API key.")
        return {
            "status": "error",
            "message": "Authentication failed. Please check your API key."
        }
        
    except Exception as e:
        print("⚠️ Unexpected error:", e)
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }

def count_tokens(text, model_name="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    return len(tokens)


def create_prompt(email_info):
    prompt = f"""
    You are an assistant that extracts job application information from email messages.

    Given the following email:
    From: {email_info['from']}
    Subject: {email_info['subject']}
    Body: {email_info['body']}

    Classify the email and return the following fields:
    - status: (string) One of ['Submitted Application', 'Rejected', 'Interview Process', 'Home Assignment', 'Accepted', 'Not Relevant'] 
    - company: The company name (string or null)
    - role: The job title or position (string or null)
    - link: A valid URL if one is included in the email (string or null)

    Return a raw JSON object with keys: status, company, role, link.
    Do NOT include explanations, extra text, or markdown formatting.
    """
    return prompt