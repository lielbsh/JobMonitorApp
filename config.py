DATABASE_URL = "sqlite:///./test.db"

APPLICATION_KEYWORDS = {
    "Submitted Application": [
        r"\byour application (was|has been)? ?sent\b",
        r"\bour team is reviewing (your|the)? details\b",
        r"\b(submitted|submission) (successfully)?\b",
        r"\bwe (have )?received your (application|cv|résumé)\b",
        r"\byour application (has been )?received\b",
    ],
    "Rejected": [
        r"\bafter (a )?careful consideration\b",
        r"\b(we|i) (deeply )?regret to inform you\b",
        r"\bwe have decided to move forward with (other|another|a different) candidate(s)?\b",
        r"\bunfortunately(,)? we\b",
        r"\bwe (will )?not be moving forward\b",
        r"\bwe('| a)?re unable to offer you\b",
    ],
    "Interview Process": [
        r"\b(to )?schedule (an )?(initial )?interview\b",
        r"\bnext steps (in|of)? the interview (process)?\b",
        r"\bschedule (a )?call\b",
        r"\bwe('| a)?re excited to move you to the next (step|stage)\b",
        r"\binvit(ed|ation) to (an )?interview\b",
        r"\bupcoming interview\b",
        r"\bmeeting (for|about) (an )?interview\b",
    ],
    "Home Assignment": [
        r"\bplease complete (the|this)? (following )?(task|assignment)\b",
        r"\byou are required to (complete|submit|solve).*assignment\b",
        r"\battached (you[' ]ll find|is) (a|the) (home|technical)? assignment\b",
        r"\byou have \d+ days? to complete (the )?assignment\b",
        r"\byou can find the task( description)? (attached|below)\b",
        r"\bexpected to take (approximately )?\d+ (hours|days)\b",
        r"\bsubmit your assignment (by|no later than)\b",
    ],
    "Offer": [
        r"\bwe (are|’re|'re) (pleased|excited) to offer you (the )?position\b",
        r"\byou (have )?received an offer\b",
        r"\bwe would like to offer you the position\b",
        r"\battached (is|you’ll find) your (offer|contract|agreement)\b",
    ]
}

LABELS = list(APPLICATION_KEYWORDS.keys())