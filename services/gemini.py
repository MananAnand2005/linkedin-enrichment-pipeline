import requests
import os

from dotenv import load_dotenv

import urllib3

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

# -----------------------------------
# Generate AI Role Summary
# -----------------------------------

def generate_role_summary(

    name,
    company,
    role_title

):

    prompt = f"""

    Person Name:
    {name}

    Company:
    {company}

    Role:
    {role_title}

    Write a short professional summary
    explaining what this person likely does.

    Keep it under 2 sentences.
    Be concise and business-focused.

    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        verify=False
    )

    # -----------------------------------
    # Error Handling
    # -----------------------------------

    if response.status_code != 200:

        print("\nGemini API Error:")
        print(response.text)

        return None

    data = response.json()

    try:

        summary = (
            data["candidates"][0]
            ["content"]["parts"][0]
            ["text"]
        )

        return summary.strip()

    except Exception as e:

        print("\nGemini Parsing Error:")
        print(str(e))

        return None