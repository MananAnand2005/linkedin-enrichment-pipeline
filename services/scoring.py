from rapidfuzz import fuzz


# -----------------------------------
# Normalize Text
# -----------------------------------

def normalize_text(text):

    if not text:
        return ""

    return (
        str(text)
        .lower()
        .strip()
    )


# -----------------------------------
# Name Match
# -----------------------------------

def score_name_match(

    input_name,
    candidate_title

):

    input_name = normalize_text(
        input_name
    )

    candidate_title = normalize_text(
        candidate_title
    )

    return fuzz.partial_ratio(
        input_name,
        candidate_title
    )


# -----------------------------------
# Company Match
# -----------------------------------

def score_company_match(

    input_company,
    snippet

):

    input_company = normalize_text(
        input_company
    )

    snippet = normalize_text(
        snippet
    )

    return fuzz.partial_ratio(
        input_company,
        snippet
    )


# -----------------------------------
# Candidate Scoring Engine
# -----------------------------------

def calculate_candidate_score(

    input_name,
    input_company,
    candidate

):

    title = candidate.get(
        "title",
        ""
    )

    snippet = candidate.get(
        "snippet",
        ""
    )

    link = candidate.get(
        "link",
        ""
    )

    total_score = 0

    signals = []

    penalties = []

    diagnostics = {}

    # -----------------------------------
    # Name Similarity
    # -----------------------------------

    raw_name_score = score_name_match(
        input_name,
        title
    )

    weighted_name_score = (
        raw_name_score * 0.4
    )

    total_score += weighted_name_score

    diagnostics[
        "name_score"
    ] = round(
        weighted_name_score,
        2
    )

    if raw_name_score >= 90:

        signals.append(
            "Strong name similarity"
        )

    elif raw_name_score >= 70:

        signals.append(
            "Moderate name similarity"
        )

    else:

        penalties.append(
            "Weak name similarity"
        )

    # -----------------------------------
    # Company Similarity
    # -----------------------------------

    raw_company_score = score_company_match(
        input_company,
        snippet
    )

    weighted_company_score = (
        raw_company_score * 0.4
    )

    total_score += weighted_company_score

    diagnostics[
        "company_score"
    ] = round(
        weighted_company_score,
        2
    )

    if raw_company_score >= 90:

        signals.append(
            "Exact company match"
        )

    elif raw_company_score >= 70:

        signals.append(
            "Partial company match"
        )

    else:

        penalties.append(
            "Weak company similarity"
        )

    # -----------------------------------
    # LinkedIn Profile Quality
    # -----------------------------------

    linkedin_bonus = 0

    if "/in/" in link:

        linkedin_bonus = 20

        total_score += linkedin_bonus

        signals.append(
            "Valid LinkedIn profile"
        )

    diagnostics[
        "linkedin_bonus"
    ] = linkedin_bonus

    # -----------------------------------
    # Final Score
    # -----------------------------------

    final_score = round(
        min(total_score, 100),
        2
    )

    diagnostics[
        "final_score"
    ] = final_score

    return {

        "confidence_score":
            final_score,

        "match_signals":
            signals,

        "penalties":
            penalties,

        "diagnostics":
            diagnostics
    }