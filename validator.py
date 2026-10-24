"""
validator.py - Validation Engine for AI Requirement Validator
------------------------------------------------------------
Coordinates individual validation rules, calculates rule-based quality scores,
compiles rule-by-rule analysis, determines validation status (PASS / NEEDS IMPROVEMENT / INVALID),
and handles saving results to CSV.
"""

import os
import csv
import datetime
import rules

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
DEFAULT_VAGUE_WORDS_FILE = os.path.join(DATA_DIR, "vague_words.txt")
DEFAULT_RESULTS_CSV = os.path.join(RESULTS_DIR, "validation_results.csv")


def generate_improved_requirement(raw_text, detected_problems):
    """
    Generates a rule-based example of an improved requirement.
    Uses clean, simple, measurable templates without introducing vague conditions.
    """
    text_lower = raw_text.lower().strip()

    if not text_lower:
        return "The system shall authenticate a valid user within 2 seconds."

    # Pattern 1: Responding quickly -> simple measurable response time
    if ("respond" in text_lower or "response" in text_lower) and ("quick" in text_lower or "fast" in text_lower or "slow" in text_lower):
        return "The system shall respond to user requests within 2 seconds."

    # Pattern 2: Fast / easy login experience
    if ("login" in text_lower or "log in" in text_lower or "authenticate" in text_lower):
        if "fast" in text_lower or "easy" in text_lower or "quick" in text_lower:
            return "The system shall authenticate a valid user within 2 seconds."
        if len(text_lower.split()) < 3:
            return "The user shall log in to the system using valid username and password credentials."

    # Pattern 3: Incomplete - Dangling preposition 'with'
    if text_lower.endswith("with") or text_lower.endswith("with."):
        return "The system shall provide users with a secure confirmation dialog."

    # Pattern 4: Incomplete - Dangling conjunction 'when', 'if', 'where'
    if text_lower.endswith("when") or text_lower.endswith("when.") or text_lower.endswith("if") or text_lower.endswith("if."):
        return "The user can log in when valid credentials are submitted."

    # Pattern 5: Incomplete - Dangling modal verb or short phrase
    if text_lower.endswith("should") or text_lower.endswith("shall") or text_lower.endswith("must"):
        return "The system shall display search results within 2 seconds."

    # Pattern 6: Incomplete phrase ending with 'to...' or ellipsis
    if "allow users to" in text_lower or text_lower.endswith("...") or text_lower.endswith("…"):
        return "The system shall allow users to reset their account password securely."

    # Pattern 7: Escape clause 'if possible'
    if "if possible" in text_lower or "where applicable" in text_lower:
        return "The system shall back up records every 24 hours at 02:00 AM."

    # Pattern 8: As soon as possible / upload / process
    if "as soon as possible" in text_lower or "asap" in text_lower:
        if "upload" in text_lower:
            return "The system shall complete file uploads within 5 seconds."
        return "The system shall process user requests within 3 seconds."

    # Pattern 9: Compound requirement (as well as)
    if "as well as" in text_lower or "in addition to" in text_lower:
        return "Requirement 1: The system shall process customer orders. Requirement 2: The system shall notify managers."

    # Pattern 10: Report generation
    if "report" in text_lower and ("generate" in text_lower or "display" in text_lower):
        return "The system shall generate a monthly report within 5 minutes."

    # Fallback template
    if detected_problems:
        return "The system shall [perform specific action] within [measurable metric, e.g., 2 seconds]."

    return "Requirement meets standard quality checks. No rewrite needed."


def validate_requirement(requirement_text, vague_words_file=None):
    """
    Main validation function.
    Runs all 10 validation rules, compiles Rule Analysis, and calculates status.
    """
    raw_text = requirement_text.strip() if requirement_text else ""

    # 1. Rule 1: Empty check
    empty_result = rules.check_empty(raw_text)
    if not empty_result["passed"]:
        rule_analysis = [
            {"name": "Empty Requirement", "passed": False, "status": "FAIL", "icon": "✗"},
            {"name": "Completeness", "passed": False, "status": "FAIL", "icon": "✗"},
            {"name": "Actor Detection", "passed": False, "status": "FAIL", "icon": "✗"},
            {"name": "Action Detection", "passed": False, "status": "FAIL", "icon": "✗"},
            {"name": "Expected Behavior", "passed": False, "status": "FAIL", "icon": "✗"},
            {"name": "Vague Words", "passed": True, "status": "PASS", "icon": "✓"},
            {"name": "Measurability", "passed": True, "status": "PASS", "icon": "✓"},
            {"name": "Ambiguity Check", "passed": True, "status": "PASS", "icon": "✓"},
            {"name": "Atomicity Check", "passed": True, "status": "PASS", "icon": "✓"},
            {"name": "Escape Clauses", "passed": True, "status": "PASS", "icon": "✓"}
        ]
        return {
            "status": "INVALID",
            "score": 0,
            "total_rules": 9,
            "problems": [empty_result],
            "suggestions": [empty_result["suggestion"]],
            "improved_requirement": "The system shall authenticate a valid user within 2 seconds.",
            "rule_analysis": rule_analysis
        }

    # Evaluate all 9 active quality rules for non-empty text
    vague_filepath = vague_words_file or DEFAULT_VAGUE_WORDS_FILE
    extra_vague = rules.load_vague_words(vague_filepath)

    res_completeness = rules.check_completeness(raw_text)
    res_actor = rules.check_actor(raw_text)
    res_action = rules.check_action(raw_text)
    res_behavior = rules.check_expected_behavior(raw_text)
    res_vague = rules.check_vague_words(raw_text, extra_vague)
    res_meas = rules.check_measurability(raw_text)
    res_ambig = rules.check_ambiguity(raw_text)
    res_atomicity = rules.check_atomicity(raw_text)
    res_escape = rules.check_escape_clauses(raw_text)

    evaluated_rules = [
        ("Completeness", res_completeness),
        ("Actor Detection", res_actor),
        ("Action Detection", res_action),
        ("Expected Behavior", res_behavior),
        ("Vague Words", res_vague),
        ("Measurability", res_meas),
        ("Ambiguity Check", res_ambig),
        ("Atomicity Check", res_atomicity),
        ("Escape Clauses", res_escape)
    ]

    total_rules = len(evaluated_rules)
    passed_count = 0
    problems = []
    suggestions = []
    rule_analysis = [
        {"name": "Empty Requirement", "passed": True, "status": "PASS", "icon": "✓"}
    ]

    for rule_name, res in evaluated_rules:
        is_passed = res["passed"]
        if is_passed:
            passed_count += 1
            rule_analysis.append({
                "name": rule_name,
                "passed": True,
                "status": "PASS",
                "icon": "✓"
            })
        else:
            icon = "⚠" if res.get("severity") in ["MEDIUM", "LOW"] else "✗"
            rule_analysis.append({
                "name": rule_name,
                "passed": False,
                "status": "FAIL",
                "icon": icon
            })
            problems.append(res)
            if res.get("suggestion") and res["suggestion"] not in suggestions:
                suggestions.append(res["suggestion"])

    # Determine status
    words = raw_text.split()
    is_too_short = len(words) < 3
    is_incomplete = bool(not res_completeness["passed"])

    if is_too_short or (is_incomplete and len(words) <= 3):
        # Truncated fragments like 'Login.' or 'The system should' are INVALID
        status = "INVALID"
    elif is_incomplete:
        # Dangling incomplete statements like 'The system shall provide users with'
        status = "NEEDS IMPROVEMENT"
    elif passed_count == total_rules:
        status = "PASS"
    else:
        # Has one or more quality defects
        status = "NEEDS IMPROVEMENT"

    improved_req = generate_improved_requirement(raw_text, problems)

    return {
        "status": status,
        "score": passed_count,
        "total_rules": total_rules,
        "problems": problems,
        "suggestions": suggestions,
        "improved_requirement": improved_req,
        "rule_analysis": rule_analysis
    }


def save_validation_result(requirement, validation_result, target_csv_path=None):
    """
    Appends a validation record to the results CSV file.
    """
    filepath = target_csv_path or DEFAULT_RESULTS_CSV
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = validation_result.get("status", "UNKNOWN")
    score = f"{validation_result.get('score', 0)}/{validation_result.get('total_rules', 0)}"

    problems_text = "; ".join([
        f"[{p.get('severity', 'MED')}] {p.get('problem_type', p.get('rule'))}: {p.get('detected', '')}"
        for p in validation_result.get("problems", [])
    ])
    suggestions_text = "; ".join(validation_result.get("suggestions", []))

    row = [
        timestamp,
        requirement.strip().replace("\n", " "),
        status,
        score,
        validation_result.get("total_rules", 0),
        problems_text if problems_text else "None",
        suggestions_text if suggestions_text else "None"
    ]

    with open(filepath, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Timestamp", "Requirement", "Status", "Score", "TotalRules", "Problems", "Suggestions"])
        writer.writerow(row)

    return filepath
