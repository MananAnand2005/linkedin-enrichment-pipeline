import requests
import os
import urllib3

from dotenv import load_dotenv

# Disable SSL warnings temporarily
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def calculate_confidence(name, company, title, snippet):

    score = 0

    if company.lower() in title.lower():
        score += 1

    first_name = name.split()[0].lower()

    if first_name in title.lower():
        score += 1

    if company.lower() in snippet.lower():
        score += 1

    return score


def search_linkedin(name, company):

    query = f'"{name}" "{company}" site:linkedin.com/in'

    url = "https://google.serper.dev/search"

    payload = {
        "q": query
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        verify=False
    )

    if response.status_code != 200:
        print("API Error:", response.text)
        return None

    data = response.json()

    organic_results = data.get("organic", [])

    if not organic_results:
        print(f"No results found for {name}")
        return None

    first_result = organic_results[0]

    title = first_result.get("title", "")
    link = first_result.get("link", "")
    snippet = first_result.get("snippet", "")

    # Validate LinkedIn profile
    if "linkedin.com/in/" not in link:
        print("Invalid LinkedIn profile")
        return None

    confidence_score = calculate_confidence(
        name,
        company,
        title,
        snippet
    )

    return {
        "name": name,
        "company": company,
        "linkedin_url": link,
        "title": title,
        "snippet": snippet,
        "confidence_score": confidence_score
    }