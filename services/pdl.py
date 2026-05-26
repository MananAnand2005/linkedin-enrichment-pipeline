import requests
import os
import urllib3

from dotenv import load_dotenv

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

load_dotenv()

PDL_API_KEY = os.getenv("PDL_API_KEY")


# -----------------------------------
# Extract Best Experience Match
# -----------------------------------

def extract_current_experience(
    experiences,
    target_company
):

    if not experiences:
        return {}

    target_company = (
        target_company or ""
    ).lower()

    # -----------------------------------
    # First try matching company
    # -----------------------------------

    for exp in experiences:

        company_name = (
            exp.get("company", {})
            .get("name", "")
        )

        company_name_lower = (
            company_name or ""
        ).lower()

        if (
            target_company
            and company_name_lower
            and target_company.split()[0]
            in company_name_lower
        ):

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


# -----------------------------------
# PDL Enrichment
# -----------------------------------

def enrich_profile(
    linkedin_url,
    company,
    preliminary_title=None
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

    # -----------------------------------
    # API Failure
    # -----------------------------------

    if response.status_code != 200:

        print(f"PDL Error: {response.text}")

        return None

    data = response.json()

    print("\n=== PDL RAW RESPONSE ===")
    print(data)

    # -----------------------------------
    # Main Person Data
    # -----------------------------------

    person_data = data.get(
        "data",
        {}
    )

    experience = person_data.get(
        "experience",
        []
    )

    # -----------------------------------
    # Extract Best Experience
    # -----------------------------------

    current_experience = extract_current_experience(
        experience,
        company
    )

    # -----------------------------------
    # Safe Current Title
    # -----------------------------------

    best_current_title = (
        current_experience.get("title")
        if current_experience
        else None
    )

    best_current_company = (
        current_experience.get("company")
        if current_experience
        else None
    )

    # -----------------------------------
    # Final Response
    # -----------------------------------

    return {

        "full_name":
            person_data.get("full_name"),

        "linkedin_url":
            linkedin_url,

        "location":
            person_data.get("location_name"),

        "pdl_job_title":
            person_data.get("job_title"),

        "best_current_title":
            best_current_title,

        "best_current_company":
            best_current_company,

        "current_experience":
            current_experience
    }