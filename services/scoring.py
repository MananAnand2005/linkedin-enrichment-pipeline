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
# Name Similarity
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
# Company Similarity
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
# Candidate Name Gate
# -----------------------------------

def passes_name_gate(

    input_name,
    candidate_title

):

    input_name = normalize_text(
        input_name
    )

    candidate_title = normalize_text(
        candidate_title
    )

    if not input_name:
        return False

    input_first_name = (
        input_name.split()[0]
    )

    # Basic first-name existence check

    if input_first_name not in candidate_title:

        return False

    # Looser fuzzy threshold

    similarity = fuzz.partial_ratio(
        input_name,
        candidate_title
    )

    return similarity >= 60


# -----------------------------------
# Main Candidate Scoring
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
    # Name Score
    # -----------------------------------

    raw_name_score = score_name_match(
        input_name,
        title
    )

    weighted_name_score = (
        raw_name_score * 0.45
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
    # Company Score
    # -----------------------------------

    raw_company_score = score_company_match(
        input_company,
        snippet
    )

    weighted_company_score = (
        raw_company_score * 0.35
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
    # LinkedIn Slug Validation
    # -----------------------------------

    linkedin_bonus = 0

    linkedin_slug = (
        link.split("/in/")[-1]
        .replace("-", " ")
        .lower()
    )

    input_first_name = (
        normalize_text(input_name)
        .split()[0]
    )

    if input_first_name in linkedin_slug:

        linkedin_bonus = 15

        total_score += linkedin_bonus

        signals.append(
            "LinkedIn slug matches first name"
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