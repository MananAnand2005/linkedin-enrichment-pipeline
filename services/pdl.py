import requests
import os
import urllib3

from dotenv import load_dotenv

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

load_dotenv()

PDL_API_KEY = os.getenv("PDL_API_KEY")


def extract_current_experience(
    experiences,
    target_company
):

    if not experiences:
        return {}

    target_company = target_company.lower()

    # -----------------------------------
    # First try company match
    # -----------------------------------
    for exp in experiences:

        company_name = (
            exp.get("company", {})
            .get("name", "")
            .lower()
        )

        if target_company.split()[0] in company_name:

            return {
                "company": company_name,
                "title": (
                    exp.get("title", {})
                    .get("name")
                )
            }

    # -----------------------------------
    # Fallback to first experience
    # -----------------------------------
    first_exp = experiences[0]

    return {
        "company": (
            first_exp.get("company", {})
            .get("name")
        ),
        "title": (
            first_exp.get("title", {})
            .get("name")
        )
    }


def enrich_profile(
    linkedin_url,
    name,
    company
):

    url = "https://api.peopledatalabs.com/v5/person/enrich"

    headers = {
        "X-API-Key": PDL_API_KEY
    }

    params = {
        "profile": linkedin_url
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        verify=False
    )

    if response.status_code != 200:

        print(f"PDL Error: {response.text}")

        return None

    data = response.json()

    print("\n=== PDL RAW RESPONSE ===")
    print(data)

    person_data = data.get("data", {})

    experience = person_data.get("experience", [])

    current_experience = extract_current_experience(
        experience,
        company
    )

    return {
        "full_name": person_data.get("full_name"),

        "linkedin_url": linkedin_url,

        "location": person_data.get("location_name"),

        "job_company":
            person_data.get("job_company_name"),

        "job_title":
            person_data.get("job_title"),

        "current_experience":
            current_experience
    }