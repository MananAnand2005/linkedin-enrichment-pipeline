import requests
import os
import urllib3

from dotenv import load_dotenv

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def calculate_confidence(
    title,
    snippet,
    company,
    name
):

    score = 0

    combined = (
        f"{title} {snippet}"
    ).lower()

    if company.lower() in combined:
        score += 2

    if name.split()[0].lower() in combined:
        score += 1

    if "linkedin" in combined:
        score += 1

    return score


def search_linkedin(
    name,
    company
):

    url = "https://google.serper.dev/search"

    payload = {
        "q": f'{name} {company} LinkedIn'
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

        print("Serper API Error")
        print(response.text)

        return None

    data = response.json()

    organic_results = data.get("organic", [])

    for result in organic_results:

        link = result.get("link", "")

        if "linkedin.com/in/" in link:

            title = result.get("title")
            snippet = result.get("snippet")

            confidence = calculate_confidence(
                title,
                snippet,
                company,
                name
            )

            return {
                "linkedin_url": link,
                "title": title,
                "snippet": snippet,
                "confidence_score": confidence
            }

    print(f"No results found for {name}")

    return None