from services.serper import search_linkedin
from services.pdl import enrich_profile
from services.gemini import generate_role_summary

from utils.excel import (
    read_input_file,
    save_output_file
)

INPUT_FILE = "input/input.xlsx"
OUTPUT_FILE = "output/output.xlsx"


def main():

    # -----------------------------------
    # Read input Excel
    # -----------------------------------
    df = read_input_file(INPUT_FILE)

    results = []

    # -----------------------------------
    # Process each row
    # -----------------------------------
    for index, row in df.iterrows():

        name = row["Name"]
        company = row["Company"]

        print(f"\nProcessing: {name} | {company}")

        # -----------------------------------
        # STEP 1: LinkedIn Discovery
        # -----------------------------------
        linkedin_result = search_linkedin(
            name,
            company
        )

        if not linkedin_result:

            print("LinkedIn discovery failed")

            continue

        linkedin_url = linkedin_result["linkedin_url"]

        # -----------------------------------
        # STEP 2: PDL Enrichment
        # -----------------------------------
        enriched_data = enrich_profile(
            linkedin_url,
            name,
            company
        )

        # -----------------------------------
        # Graceful fallback if PDL fails
        # -----------------------------------
        if not enriched_data:

            enriched_data = {
                "job_title": None,
                "current_experience": {}
            }

        # -----------------------------------
        # Safe extraction
        # -----------------------------------
        current_exp = (
            enriched_data.get("current_experience")
            or {}
        )

        # -----------------------------------
        # Resolve best title
        # -----------------------------------
        best_title = (

            current_exp.get("title")

            or enriched_data.get("job_title")

            or linkedin_result.get("title")
        )

        # -----------------------------------
        # Industry fallback
        # -----------------------------------
        industry = "Financial Services"

        # -----------------------------------
        # STEP 3: Gemini Role Summary
        # -----------------------------------
        role_summary = generate_role_summary(
            name=name,
            company=company,
            title=best_title,
            industry=industry
        )

        # -----------------------------------
        # Final combined output
        # -----------------------------------
        final_result = {

            "name": name,

            "company": company,

            "linkedin_url":
                linkedin_result.get("linkedin_url"),

            "headline_title":
                linkedin_result.get("title"),

            "headline_snippet":
                linkedin_result.get("snippet"),

            "pdl_job_title":
                enriched_data.get("job_title"),

            "best_current_title":
                current_exp.get("title"),

            "best_current_company":
                current_exp.get("company"),

            "confidence_score":
                linkedin_result.get("confidence_score"),

            "role_summary":
                role_summary
        }

        results.append(final_result)

        print("Completed successfully")

    # -----------------------------------
    # Save output Excel
    # -----------------------------------
    save_output_file(
        results,
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()