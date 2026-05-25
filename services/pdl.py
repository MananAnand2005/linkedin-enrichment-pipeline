import requests
import os
import urllib3

from dotenv import load_dotenv

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

load_dotenv()

PDL_API_KEY = os.getenv("PDL_API_KEY")


def extract_current_experience(experience_list, target_company):
    """
    Find the best matching current experience
    """

    if not experience_list:
        return None

    target_company = target_company.lower()

    for exp in experience_list:

        company_name = (
            exp.get("company", {}).get("name", "")
        ).lower()

        is_current = exp.get("is_primary", False)

        # Match target company
        if target_company in company_name:

            return {
                "company": exp.get("company", {}).get("name"),
                "title": exp.get("title", {}).get("name"),
                "start_date": exp.get("start_date"),
                "end_date": exp.get("end_date"),
                "is_primary": is_current
            }

    # Fallback: first experience
    first_exp = experience_list[0]

    return {
        "company": first_exp.get("company", {}).get("name"),
        "title": first_exp.get("title", {}).get("name"),
        "start_date": first_exp.get("start_date"),
        "end_date": first_exp.get("end_date"),
        "is_primary": first_exp.get("is_primary")
    }


def enrich_profile(
    linkedin_url,
    full_name,
    target_company
    ):

    url = "https://api.peopledatalabs.com/v5/person/enrich"

    headers = {
        "X-Api-Key": PDL_API_KEY
    }

    params = {
    "profile": linkedin_url,
    "name": full_name,
    "company": target_company
    }

    response = requests.get(
    url,
    headers=headers,
    params=params,
    verify=False
    )

    if response.status_code != 200:
        print("PDL Error:", response.text)
        return None

    data = response.json()
    person_data = data.get("data", {})

    print("\n=== PDL RAW RESPONSE ===")
    print(data)

    experience = person_data.get("experience", [])

    current_experience = extract_current_experience(
        experience,
        target_company
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