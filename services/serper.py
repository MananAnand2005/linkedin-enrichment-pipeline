import requests
import os
import urllib3
import json
from dotenv import load_dotenv

from services.scoring import (
    calculate_candidate_score
)

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

load_dotenv()

SERPER_API_KEY = os.getenv(
    "SERPER_API_KEY"
)


def search_linkedin(
    name,
    company
):

    url = "https://google.serper.dev/search"

    payload = {
        "q": f"{name} {company} LinkedIn"
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

        print("\n=== SERPER API ERROR ===")
        print(response.text)

        return None

    data = response.json()

    organic_results = data.get(
        "organic",
        []
    )

    # -----------------------------------
    # Collect Candidate Profiles
    # -----------------------------------

    linkedin_candidates = []

    for result in organic_results:

        link = result.get(
            "link",
            ""
        )

        # Only consider personal LinkedIn profiles

        if "linkedin.com/in/" not in link:
            continue

        title = result.get(
            "title",
            ""
        )

        snippet = result.get(
            "snippet",
            ""
        )

        # -----------------------------------
        # Score Candidate
        # -----------------------------------

        score_data = calculate_candidate_score(

        input_name=name,

        input_company=company,

         candidate=result
        )

        score = score_data[
        "confidence_score"
        ]

        signals = score_data[
        "match_signals"
        ]

        penalties = score_data[
       "penalties"
        ]

        diagnostics = score_data[
        "diagnostics"
        ]

        candidate_data = {

            "linkedin_url": link,

            "title": title,

            "snippet": snippet,

            "confidence_score": score,
            "match_signals": signals,
            "penalties": penalties,
            "diagnostics": diagnostics
        }

        linkedin_candidates.append(
            candidate_data
        )

    # -----------------------------------
    # No Candidates Found
    # -----------------------------------

    if not linkedin_candidates:

        print(
            f"\nNo LinkedIn results found for {name}"
        )

        return None

    # -----------------------------------
    # Sort By Confidence
    # -----------------------------------

    linkedin_candidates = sorted(

        linkedin_candidates,

        key=lambda x:
        x["confidence_score"],

        reverse=True
    )

    # -----------------------------------
    # Best Match
    # -----------------------------------

    best_candidate = linkedin_candidates[0]

    print("\n=== BEST MATCH ===")

    print(best_candidate)

    print(
        json.dumps(
            best_candidate,
            indent=4
        )
    )

    # -----------------------------------
    # Optional:
    # Show Top Candidates
    # -----------------------------------



    print("\n=== TOP CANDIDATES ===")

    for idx, candidate in enumerate(
        linkedin_candidates[:5],
        start=1
    ):

     print(
        f"\n========== Candidate #{idx} =========="
    )

    print(
        json.dumps(
            candidate,
            indent=4
        )
    )
    return best_candidate