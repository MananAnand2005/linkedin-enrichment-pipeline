import requests
import os
import urllib3
import json

from dotenv import load_dotenv

from services.scoring import (
    calculate_candidate_score,
    passes_name_gate
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

    # -----------------------------------
    # API Failure
    # -----------------------------------

    if response.status_code != 200:

        print("\n=== SERPER API ERROR ===")

        print(response.text)

        return None

    data = response.json()

    organic_results = data.get(
        "organic",
        []
    )

    linkedin_candidates = []

    # -----------------------------------
    # Candidate Extraction
    # -----------------------------------

    for result in organic_results:

        link = result.get(
            "link",
            ""
        )

        # Only personal LinkedIn profiles

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
        # Soft Name Gate
        # -----------------------------------

        if not passes_name_gate(
            name,
            title
        ):

            continue

        # -----------------------------------
        # Candidate Scoring
        # -----------------------------------

        score_data = calculate_candidate_score(

            input_name=name,

            input_company=company,

            candidate=result
        )

        candidate_data = {

            "linkedin_url": link,

            "title": title,

            "snippet": snippet,

            "confidence_score":
                score_data[
                    "confidence_score"
                ],

            "match_signals":
                score_data[
                    "match_signals"
                ],

            "penalties":
                score_data[
                    "penalties"
                ],

            "diagnostics":
                score_data[
                    "diagnostics"
                ]
        }

        linkedin_candidates.append(
            candidate_data
        )

    # -----------------------------------
    # No Candidates
    # -----------------------------------

    if not linkedin_candidates:

        print(
            f"\nNo LinkedIn results found for {name}"
        )

        return None

    # -----------------------------------
    # Sort Candidates
    # -----------------------------------

    linkedin_candidates = sorted(

        linkedin_candidates,

        key=lambda x:
        x["confidence_score"],

        reverse=True
    )

    best_candidate = linkedin_candidates[0]

    # -----------------------------------
    # Lower Threshold
    # -----------------------------------

    if best_candidate[
        "confidence_score"
    ] < 55:

        print(
            "\nRejected low-confidence match"
        )

        return None

    # -----------------------------------
    # Debug Logs
    # -----------------------------------

    print("\n=== BEST MATCH ===")

    print(
        json.dumps(
            best_candidate,
            indent=4
        )
    )

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