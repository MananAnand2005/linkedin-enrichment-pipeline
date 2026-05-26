from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.models import EnrichmentRequest

from services.serper import search_linkedin
from services.pdl import enrich_profile
from services.gemini import generate_role_summary

import pandas as pd
import uuid
import os

app = FastAPI()

# -----------------------------------
# CORS
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# Health Check
# -----------------------------------

@app.get("/health")
def health():

    return {
        "status": "running"
    }

# -----------------------------------
# Upload Excel
# -----------------------------------

@app.post("/upload-excel")
async def upload_excel(

    file: UploadFile = File(...)

):

    try:

        df = pd.read_excel(file.file)

        df = df.dropna(how="all")

        df = df.where(
            pd.notnull(df),
            None
        )

        rows = df.to_dict(
            orient="records"
        )

        return {
            "rows": rows,
            "total_rows": len(rows)
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# -----------------------------------
# Enrich Single Lead
# -----------------------------------

@app.post("/enrich-lead")
async def enrich_lead(

    payload: dict

):

    try:

        row = payload.get("row", {})

        name = (
            row.get("Name")
            or row.get("name")
            or ""
        )

        company = (
            row.get("Company")
            or row.get("company")
            or ""
        )

        print(f"\nProcessing: {name} | {company}")

        # -----------------------------------
        # Serper
        # -----------------------------------

        linkedin_data = search_linkedin(
            name,
            company
        )

        if not linkedin_data:

            return {

                **row,

                "status": "LinkedIn Not Found"
            }

        linkedin_url = linkedin_data.get(
            "linkedin_url"
        )

        # -----------------------------------
        # PDL
        # -----------------------------------

        pdl_data = enrich_profile(
            linkedin_url,
            company
        )

        role_title = None

        if pdl_data:

            role_title = (
                pdl_data.get("best_current_title")
                or pdl_data.get("pdl_job_title")
            )

        # -----------------------------------
        # Gemini
        # -----------------------------------

        role_summary = None

        if role_title:

            role_summary = generate_role_summary(
                name=name,
                company=company,
                role_title=role_title
            )

        # -----------------------------------
        # Final Output
        # -----------------------------------

        return {

        **row,

          "linkedin_url":
           linkedin_url,

         "role_title":
         role_title,

         "role_summary":
         role_summary,

         "confidence_score":
         linkedin_data.get(
            "confidence_score"
         ),

         "match_signals":
          ", ".join(
            linkedin_data.get(
                "match_signals",
                []
            )
         ),

    "status":
        "Completed"
}

    except Exception as e:

        print(str(e))

        return {

            **row,

            "status": "Failed",

            "error": str(e)
        }

# -----------------------------------
# Export Excel
# -----------------------------------

@app.post("/export-excel")
async def export_excel(

    payload: EnrichmentRequest

):

    try:

        df = pd.DataFrame(
            payload.rows
        )

        os.makedirs(
            "exports",
            exist_ok=True
        )

        filename = (
            f"exports/enriched_"
            f"{uuid.uuid4().hex[:8]}.xlsx"
        )

        df.to_excel(
            filename,
            index=False
        )

        return FileResponse(
            path=filename,
            filename="enriched_results.xlsx",
            media_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )

    except Exception as e:

        return {
            "error": str(e)
        }