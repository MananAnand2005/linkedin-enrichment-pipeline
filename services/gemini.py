import requests
import os
import urllib3

from dotenv import load_dotenv

# Disable SSL warnings temporarily
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generate_role_summary(
    name,
    company,
    title,
    industry
):

    # -----------------------------------
    # Safety fallback
    # -----------------------------------
    if not title:

        return "No role title available"

    # -----------------------------------
    # Gemini endpoint
    # -----------------------------------
    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1beta/models/gemini-3.1-flash-lite:generateContent?key={GEMINI_API_KEY}"
    )

    # -----------------------------------
    # Prompt
    # -----------------------------------
    prompt = f"""
You are analyzing corporate professionals.

Based on the following structured profile data,
explain what this person likely does in their role.

Be specific to the function and industry.
Avoid generic corporate jargon.
Keep response under 60 words.

Name: {name}
Company: {company}
Role: {title}
Industry: {industry}
"""

    # -----------------------------------
    # Request payload
    # -----------------------------------
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

    # -----------------------------------
    # API request
    # -----------------------------------
    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            verify=False
        )

    except Exception as e:

        print("\nGemini Connection Error:")
        print(e)

        return "Gemini connection failed"

    # -----------------------------------
    # Handle non-200 responses
    # -----------------------------------
    if response.status_code != 200:

        print("\nGemini API Error:")
        print(response.text)

        return "Gemini summary failed"

    # -----------------------------------
    # Parse response
    # -----------------------------------
    try:

        data = response.json()

        summary = (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

        return summary.strip()

    except Exception as e:

        print("\nGemini Parsing Error:")
        print(e)

        return "Gemini parsing failed"