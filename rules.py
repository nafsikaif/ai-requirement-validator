"""
rules.py - Modular Validation Rules for AI Requirement Validator
----------------------------------------------------------------
Provides rule-based inspections for software requirements:
1. Empty requirement check
2. Length & Completeness check (robust detection of dangling prepositions,
   conjunctions, modals, and trailing ellipses)
3. Actor detection (recognizing 'system' and human actors)
4. Action detection (covering verbs like 'respond', 'process', and modal+verb patterns)
5. Expected behavior (modal verb check)
6. Categorized vague word detection (Performance, Quantity, Time, Quality)
7. Measurability check
8. Ambiguity check
9. Atomicity check (detecting compounded / multi-part requirements)
10. Escape clause / loophole detection (detecting untestable exceptions like 'if possible')

Every rule returns a structured dictionary including pass status, severity,
problem category, detected text, explanation ('why'), and suggestion.
"""

import os
import re

# Categorized dictionary of vague and qualitative terms
VAGUE_CATEGORIES = {
    "Performance": {
        "words": [
            "fast", "quick", "quickly", "slow", "rapid", "efficient",
            "efficiently", "high-performance", "instant", "instantaneous"
        ],
        "why": "The term does not define a measurable response time or quantifiable speed metric.",
        "suggestion": "Specify a measurable response time (e.g., 'within 2 seconds')."
    },
    "Quantity": {
        "words": [
            "many", "few", "some", "several", "most", "minimal",
            "optimum", "optimal"
        ],
        "why": "The term does not specify an exact quantity or boundary condition.",
        "suggestion": "Specify an exact count or boundary (e.g., 'at least 100 records' or 'up to 50 concurrent users')."
    },
    "Time": {
        "words": [
            "soon", "later", "immediately", "as soon as possible",
            "asap", "timely"
        ],
        "why": "The term does not establish an exact deadline or timeframe.",
        "suggestion": "Specify a definite timeframe (e.g., 'within 5 minutes' or 'within 24 hours')."
    },
    "Quality": {
        "words": [
            "easy", "simple", "user-friendly", "user friendly",
            "convenient", "conveniently", "appropriate", "appropriately",
            "reasonable", "reasonably", "adequate", "adequately",
            "reliable", "robust", "flexible", "seamless", "seamlessly",
            "intuitive", "sufficient", "sufficiently"
        ],
        "why": "The term is subjective and cannot be objectively verified during acceptance testing.",
        "suggestion": "Define verifiable acceptance criteria (e.g., 'completed in 3 steps or fewer')."
    }
}

# Recognized system and human actors
COMMON_ACTORS = [
    "system", "application", "software", "platform", "service", "server",
    "user", "users", "admin", "admins", "administrator", "administrators",
    "customer", "customers", "client", "clients", "employee", "employees",
    "manager", "managers", "guest", "guests", "visitor", "visitors",
    "operator", "operators", "agent", "actor"
]

# Action verbs commonly expected in software requirements
COMMON_ACTIONS = [
    "respond", "process", "retrieve", "authenticate", "provide", "accept",
    "reject", "handle", "receive", "return", "support", "allow", "manage",
    "display", "generate", "calculate", "send", "store", "update", "delete",
    "create", "search", "upload", "download", "login", "log in", "logout",
    "log out", "register", "submit", "sign up", "sign in", "show", "compute",
    "transmit", "save", "modify", "remove", "add", "find", "validate",
    "verify", "notify", "view", "fetch", "export", "import", "reset",
    "render", "redirect", "record", "execute"
]

# Modal verbs indicating requirement constraints
MODAL_VERBS = ["shall", "should", "must", "will", "can", "may"]

# Dangling terminal words that indicate an incomplete statement
DANGLING_TERMINAL_WORDS = {
    # Prepositions
    "with", "for", "in", "to", "at", "by", "from", "into", "onto", "upon",
    "about", "than", "of", "through", "toward", "towards", "without",
    # Conjunctions & Subordinators
    "and", "or", "but", "if", "when", "while", "as", "because", "unless",
    "after", "before", "so", "whether", "where", "whenever", "whereas",
    "although", "since", "until", "that", "which",
    # Auxiliary & Modal verbs hanging at end
    "shall", "should", "must", "will", "can", "may", "could", "would", "might",
    "be", "is", "are", "was", "were", "been", "have", "has", "had"
}

# Ambiguous phrases and idioms
AMBIGUOUS_PATTERNS = [
    (r"\bas soon as possible\b", "as soon as possible"),
    (r"\basap\b", "asap"),
    (r"\betc\.?\b", "etc."),
    (r"\band/or\b", "and/or"),
    (r"\band so on\b", "and so on"),
    (r"\bsome users\b", "some users"),
    (r"\bmany users\b", "many users"),
    (r"\bnormally\b", "normally"),
    (r"\busually\b", "usually"),
    (r"\btbd\b", "tbd"),
    (r"\bto be determined\b", "to be determined")
]

# Escape clauses that create non-verifiable loopholes
ESCAPE_CLAUSE_PATTERNS = [
    (r"\bif possible\b", "if possible"),
    (r"\bwhere applicable\b", "where applicable"),
    (r"\bwhere appropriate\b", "where appropriate"),
    (r"\bas appropriate\b", "as appropriate"),
    (r"\bto the extent possible\b", "to the extent possible"),
    (r"\bsubject to change\b", "subject to change"),
    (r"\bunless not feasible\b", "unless not feasible"),
    (r"\bat user'?s? discretion\b", "at user discretion"),
    (r"\bif practical\b", "if practical")
]


def load_vague_words(filepath=None):
    """
    Loads custom vague words from a file if present, returning a flat list.
    """
    words = set()
    for cat in VAGUE_CATEGORIES.values():
        words.update(cat["words"])

    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    cleaned = line.strip().lower()
                    if cleaned and not cleaned.startswith("#"):
                        words.add(cleaned)
        except Exception:
            pass

    return sorted(list(words))


# =====================================================================
# RULE 1: EMPTY REQUIREMENT CHECK
# =====================================================================
def check_empty(requirement):
    """
    Rule 1: Check if input is empty or whitespace only.
    Severity: HIGH
    """
    if not requirement or not requirement.strip():
        return {
            "passed": False,
            "rule": "Empty Requirement Check",
            "problem_type": "Empty Requirement",
            "detected": "None (empty input)",
            "why": "No requirement text was provided.",
            "suggestion": "Enter a complete software requirement.",
            "severity": "HIGH",
            "message": "Requirement is empty."
        }
    return {
        "passed": True,
        "rule": "Empty Requirement Check",
        "problem_type": None,
        "detected": None,
        "why": None,
        "suggestion": None,
        "severity": None,
        "message": None
    }


# =====================================================================
# RULE 2: LENGTH & COMPLETENESS CHECK (ROBUST)
# =====================================================================
def check_completeness(requirement, min_words=3):
    """
    Rule 2: Detect incomplete statements, truncated sentences, dangling prepositions,
    dangling conjunctions, or trailing ellipses.
    Severity: HIGH
    """
    stripped = requirement.strip()

    # 1. Check for trailing ellipses or dashes: e.g. "The system should allow users to..."
    if re.search(r"(\.{2,}|…|--)$", stripped):
        return {
            "passed": False,
            "rule": "Length and Completeness",
            "problem_type": "Incomplete Requirement (Trailing Ellipsis)",
            "detected": "Premature ending ('...' or ellipsis)",
            "why": "The requirement terminates abruptly without defining the complete action or outcome.",
            "suggestion": "Complete the requirement sentence specifying the intended system behavior.",
            "severity": "HIGH",
            "message": "Requirement is incomplete or ends abruptly with an ellipsis."
        }

    # Extract clean alphanumeric tokens
    words = re.findall(r"\b[\w-]+\b", stripped)

    # 2. Check minimum length
    if len(words) < min_words:
        return {
            "passed": False,
            "rule": "Length and Completeness",
            "problem_type": "Incomplete Requirement (Too Short)",
            "detected": f"{len(words)} word(s)",
            "why": "The input is too brief to describe a complete system requirement.",
            "suggestion": "Provide a complete requirement sentence (e.g., 'The user shall log in using valid credentials.').",
            "severity": "HIGH",
            "message": f"Requirement is too short ({len(words)} word(s)) to describe complete system behavior."
        }

    # 3. Check for dangling terminal words (prepositions, conjunctions, hanging modals)
    last_word = words[-1].lower() if words else ""
    if last_word in DANGLING_TERMINAL_WORDS:
        return {
            "passed": False,
            "rule": "Length and Completeness",
            "problem_type": "Incomplete Requirement (Dangling Clause)",
            "detected": f"Dangling terminal word: '{last_word}'",
            "why": f"The sentence ends prematurely on '{last_word}' without providing the target object, condition, or clause.",
            "suggestion": f"Complete the statement by providing what follows '{last_word}' (e.g., specify the target object, condition, or outcome).",
            "severity": "HIGH",
            "message": f"Incomplete statement: ends with dangling '{last_word}'."
        }

    # 4. Check for dangling infinitive phrases: e.g., "required to", "able to"
    if re.search(r"\b(able to|allowed to|required to|supposed to|in order to|such as|intended to)[.,;]?$", stripped, re.IGNORECASE):
        match = re.search(r"\b(able to|allowed to|required to|supposed to|in order to|such as|intended to)[.,;]?$", stripped, re.IGNORECASE)
        dangling_phrase = match.group(1)
        return {
            "passed": False,
            "rule": "Length and Completeness",
            "problem_type": "Incomplete Requirement (Dangling Phrase)",
            "detected": f"Dangling phrase: '{dangling_phrase}'",
            "why": f"The requirement terminates on '{dangling_phrase}' without defining the intended action.",
            "suggestion": "Complete the sentence by specifying the intended system behavior following this phrase.",
            "severity": "HIGH",
            "message": f"Incomplete statement: ends with '{dangling_phrase}'."
        }

    return {
        "passed": True,
        "rule": "Length and Completeness",
        "problem_type": None,
        "detected": None,
        "why": None,
        "suggestion": None,
        "severity": None,
        "message": None
    }


# =====================================================================
# RULE 3: ACTOR DETECTION
# =====================================================================
def check_actor(requirement):
    """
    Rule 3: Check whether requirement specifies an actor or initiator.
    Recognizes 'system', 'user', 'administrator', 'admin', 'customer', etc.
    """
    text_lower = requirement.lower()

    for actor in COMMON_ACTORS:
        pattern = r"\b" + re.escape(actor) + r"\b"
        if re.search(pattern, text_lower):
            return {
                "passed": True,
                "rule": "Actor Detection",
                "problem_type": None,
                "detected": actor,
                "why": None,
                "suggestion": None,
                "severity": None,
                "message": None
            }

    match = re.search(r"\b(the|a|an)\s+([a-z_]+)\s+(shall|should|must|can|will)\b", text_lower)
    if match:
        return {
            "passed": True,
            "rule": "Actor Detection",
            "problem_type": None,
            "detected": match.group(2),
            "why": None,
            "suggestion": None,
            "severity": None,
            "message": None
        }

    return {
        "passed": False,
        "rule": "Actor Detection",
        "problem_type": "Actor Missing / Unspecified",
        "detected": "No actor identified",
        "why": "Actor/user is not explicitly specified in the requirement.",
        "suggestion": "Specify who or what initiates or performs the action (e.g., 'The system shall...', 'The user shall...').",
        "severity": "LOW",
        "message": "Actor/user is not explicitly specified."
    }


# =====================================================================
# RULE 4: ACTION DETECTION
# =====================================================================
def check_action(requirement):
    """
    Rule 4: Verify whether requirement contains an identifiable system action.
    Includes verbs like respond, process, retrieve, authenticate, provide, etc.
    Also recognizes contextual patterns like: '<actor> <modal> <verb>'.
    """
    text_lower = requirement.lower()

    for action in COMMON_ACTIONS:
        pattern = r"\b" + re.escape(action) + r"\b"
        if re.search(pattern, text_lower):
            return {
                "passed": True,
                "rule": "Action Detection",
                "problem_type": None,
                "detected": action,
                "why": None,
                "suggestion": None,
                "severity": None,
                "message": None
            }

    pattern = r"\b(?:the\s+)?(?:system|user|administrator|admin|customer|client|employee|manager)\s+(?:shall|should|must|can|will)\s+([a-z]+)\b"
    match = re.search(pattern, text_lower)
    if match:
        detected_word = match.group(1)
        if detected_word not in ["not", "be", "have", "a", "an", "the"]:
            return {
                "passed": True,
                "rule": "Action Detection",
                "problem_type": None,
                "detected": detected_word,
                "why": None,
                "suggestion": None,
                "severity": None,
                "message": None
            }

    modal_verb_match = re.search(r"\b(?:shall|should|must|can|will)\s+([a-z]+)\b", text_lower)
    if modal_verb_match:
        cand = modal_verb_match.group(1)
        if cand not in ["not", "be", "have", "the", "a", "an"]:
            return {
                "passed": True,
                "rule": "Action Detection",
                "problem_type": None,
                "detected": cand,
                "why": None,
                "suggestion": None,
                "severity": None,
                "message": None
            }

    return {
        "passed": False,
        "rule": "Action Detection",
        "problem_type": "Unclear System Action",
        "detected": "No recognized action verb",
        "why": "System action is unclear or missing from the requirement statement.",
        "suggestion": "Specify what the system or user must do using a clear verb (e.g., 'respond', 'authenticate', 'generate').",
        "severity": "HIGH",
        "message": "System action is unclear or missing."
    }


# =====================================================================
# RULE 5: EXPECTED BEHAVIOR (MODAL VERBS)
# =====================================================================
def check_expected_behavior(requirement):
    """
    Rule 5: Verify whether requirement uses standard modal verbs
    such as 'shall', 'should', 'must', 'can', 'will'.
    Severity: HIGH
    """
    text_lower = requirement.lower()

    for modal in MODAL_VERBS:
        pattern = r"\b" + re.escape(modal) + r"\b"
        if re.search(pattern, text_lower):
            return {
                "passed": True,
                "rule": "Expected Behavior (Modal Verb)",
                "problem_type": None,
                "detected": modal,
                "why": None,
                "suggestion": None,
                "severity": None,
                "message": None
            }

    return {
        "passed": False,
        "rule": "Expected Behavior (Modal Verb)",
        "problem_type": "Missing Expected Behavior",
        "detected": "No modal verb ('shall', 'should', 'must')",
        "why": "Standard requirements syntax requires a modal verb to designate mandatory or expected behavior.",
        "suggestion": "State expected behavior clearly using requirement modal verbs (e.g., 'The system shall...').",
        "severity": "HIGH",
        "message": "The expected system behavior is unclear (missing modal verb such as 'shall', 'should', or 'must')."
    }


# =====================================================================
# RULE 6: VAGUE WORD DETECTION (CATEGORIZED)
# =====================================================================
def check_vague_words(requirement, extra_vague_words=None):
    """
    Rule 6: Detect vague words categorized into Performance, Quantity, Time, Quality.
    Severity: MEDIUM
    """
    text_lower = requirement.lower()
    problems_found = []

    for category_name, cat_data in VAGUE_CATEGORIES.items():
        for word in cat_data["words"]:
            pattern = r"\b" + re.escape(word) + r"\b"
            if re.search(pattern, text_lower):
                problems_found.append({
                    "category": category_name,
                    "word": word,
                    "why": cat_data["why"],
                    "suggestion": cat_data["suggestion"]
                })

    if problems_found:
        first = problems_found[0]
        detected_list = [f"'{p['word']}'" for p in problems_found]
        return {
            "passed": False,
            "rule": "Vague Words Check",
            "problem_type": f"Vague {first['category']} Term",
            "detected": ", ".join(detected_list),
            "why": first["why"],
            "suggestion": first["suggestion"],
            "severity": "MEDIUM",
            "message": f"Vague {first['category'].lower()} term detected: {', '.join(detected_list)}",
            "all_detected": problems_found
        }

    return {
        "passed": True,
        "rule": "Vague Words Check",
        "problem_type": None,
        "detected": None,
        "why": None,
        "suggestion": None,
        "severity": None,
        "message": None,
        "all_detected": []
    }


# =====================================================================
# RULE 7: MEASURABILITY CHECK
# =====================================================================
def check_measurability(requirement):
    """
    Rule 7: Look for measurable information when performance or capacity is discussed.
    Severity: MEDIUM
    """
    text_lower = requirement.lower()

    perf_keywords = [
        "fast", "quick", "quickly", "slow", "speed", "respond", "response",
        "latency", "throughput", "load", "capacity", "duration",
        "delay", "performance", "efficient", "efficiently", "uptime"
    ]

    has_perf_context = any(
        re.search(r"\b" + re.escape(kw) + r"\b", text_lower) for kw in perf_keywords
    )

    measurement_patterns = [
        r"\b\d+(\.\d+)?\s*(seconds?|sec|s|minutes?|min|hours?|hrs?|ms|milliseconds?)\b",
        r"\b\d+(\.\d+)?\s*(%|percent)\b",
        r"\b\d+\s*(users?|records?|items?|transactions?|requests?|items?|entries)\b",
        r"\b\d+(\.\d+)?\s*(mb|gb|kb|tb)\b",
        r"\bwithin\s+\d+",
        r"\bmaximum\s+\d+",
        r"\bat least\s+\d+",
        r"\bless than\s+\d+",
        r"\bmore than\s+\d+"
    ]

    has_measurement = any(re.search(pat, text_lower) for pat in measurement_patterns)

    if has_perf_context and not has_measurement:
        return {
            "passed": False,
            "rule": "Measurability Check",
            "problem_type": "Non-Measurable Performance Criterion",
            "detected": "Performance/responsiveness criteria without numeric metrics",
            "why": "The requirement states performance or timing expectations without measurable values.",
            "suggestion": "Specify a measurable response time, such as 'within 2 seconds' or 'within 500 ms'.",
            "severity": "MEDIUM",
            "message": "Performance/responsiveness criteria lack quantifiable metrics."
        }

    return {
        "passed": True,
        "rule": "Measurability Check",
        "problem_type": None,
        "detected": None,
        "why": None,
        "suggestion": None,
        "severity": None,
        "message": None
    }


# =====================================================================
# RULE 8: AMBIGUITY CHECK
# =====================================================================
def check_ambiguity(requirement):
    """
    Rule 8: Detect predefined ambiguous phrases like 'etc.', 'and/or', 'as soon as possible'.
    Severity: MEDIUM
    """
    text_lower = requirement.lower()
    found_ambiguities = []

    for pattern, label in AMBIGUOUS_PATTERNS:
        if re.search(pattern, text_lower):
            found_ambiguities.append(label)

    if found_ambiguities:
        formatted = ", ".join([f"'{item}'" for item in found_ambiguities])
        return {
            "passed": False,
            "rule": "Ambiguity Check",
            "problem_type": "Ambiguous Phrase",
            "detected": formatted,
            "why": f"Phrases like {formatted} introduce subjective interpretation and lack precise boundaries.",
            "suggestion": "Remove ambiguous phrasing such as 'etc.' or 'as soon as possible' and specify exact conditions.",
            "severity": "MEDIUM",
            "message": f"Ambiguous phrase(s) detected: {formatted}"
        }

    return {
        "passed": True,
        "rule": "Ambiguity Check",
        "problem_type": None,
        "detected": None,
        "why": None,
        "suggestion": None,
        "severity": None,
        "message": None
    }


# =====================================================================
# RULE 9: ATOMICITY CHECK (NEW: SINGLE REQUIREMENT RULE)
# =====================================================================
def check_atomicity(requirement):
    """
    Rule 9: Check whether the requirement is atomic (describes one capability).
    Detects compounded clauses like 'as well as the system shall...', 'in addition to'.
    Severity: MEDIUM
    """
    text_lower = requirement.lower()

    # Detect compounding conjunctive phrases
    compounds = []
    if "as well as" in text_lower:
        compounds.append("as well as")
    if "in addition to" in text_lower:
        compounds.append("in addition to")
    if "and also" in text_lower:
        compounds.append("and also")

    # Detect multiple modal clauses (e.g., "shall... and shall...")
    modal_count = len(re.findall(r"\b(shall|should|must)\b", text_lower))

    if compounds or modal_count >= 2:
        detected_reason = f"Multiple clauses linked with '{compounds[0]}'" if compounds else f"{modal_count} separate modal obligations ('shall/should/must')"
        return {
            "passed": False,
            "rule": "Atomicity Check",
            "problem_type": "Non-Atomic Requirement (Compound Statement)",
            "detected": detected_reason,
            "why": "Requirements should be atomic (specifying a single distinct capability). Multi-part requirements are harder to verify and test.",
            "suggestion": "Split this compound statement into separate, atomic requirement statements.",
            "severity": "MEDIUM",
            "message": "Requirement combines multiple distinct obligations into a single sentence."
        }

    return {
        "passed": True,
        "rule": "Atomicity Check",
        "problem_type": None,
        "detected": None,
        "why": None,
        "suggestion": None,
        "severity": None,
        "message": None
    }


# =====================================================================
# RULE 10: ESCAPE CLAUSE & LOOPHOLE DETECTION (NEW)
# =====================================================================
def check_escape_clauses(requirement):
    """
    Rule 10: Detect escape clauses like 'if possible', 'where applicable', etc.
    Severity: MEDIUM
    """
    text_lower = requirement.lower()
    found_escapes = []

    for pattern, label in ESCAPE_CLAUSE_PATTERNS:
        if re.search(pattern, text_lower):
            found_escapes.append(label)

    if found_escapes:
        formatted = ", ".join([f"'{item}'" for item in found_escapes])
        return {
            "passed": False,
            "rule": "Escape Clause Check",
            "problem_type": "Escape Clause / Loophole Detected",
            "detected": formatted,
            "why": f"Escape clauses such as {formatted} create untestable loopholes where compliance can be skipped.",
            "suggestion": f"Remove {formatted} and define explicit, testable criteria for when the behavior is required.",
            "severity": "MEDIUM",
            "message": f"Escape clause detected: {formatted}"
        }

    return {
        "passed": True,
        "rule": "Escape Clause Check",
        "problem_type": None,
        "detected": None,
        "why": None,
        "suggestion": None,
        "severity": None,
        "message": None
    }
