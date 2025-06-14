DATABASE_URL = "sqlite:///./JobMonitorApp.db"

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

EXTRACTION_PATTERNS = [
    (r"application for (.+?) at ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "role_company"),
    (r"for the ([A-Za-z0-9\- &_]+) role at ([A-Z][a-zA-Z0-9&.\-']+?)(?=[\s\.,]|$)", "role_company"),
    (r"for the ([A-Za-z0-9\- &_]+) position at ([A-Z][a-zA-Z& .\-']+?)(?=[\s\.,]|$)", "role_company"),
    (r"has been received by ([A-Z][a-zA-Z& .\-']{2,}) for the ([A-Za-z0-9\- &_]+) (?:position|role)\b", "company_role"),
    (r"sent to ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "company"),
    (r"thanks for applying to ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "company"),
    (r"Thank you for applying to ([A-Z][a-zA-Z& .\-']{2,})(?=[\s\.,]|$)", "company"),
    (r"\b([A-Z][\w&.\-']{1,50})\s+(HR Team|Recruiting Team|HR)\b", "company"),
    (r"\b([A-Z][\w&.\-']{1,50})'s\s+(Talent Team|HR Team|Recruiting Team)\b", "company"),
    (r"for the role of ([A-Za-z0-9\- &_]{2,})", "role"),
    (r"for the ([A-Za-z0-9&\-.,' ]+?) position", "role"),
    (r"position of ([A-Za-z0-9\- &_]{2,})", "role"),
    (r"application for ([A-Z][a-zA-Z0-9\- &]+)(?:\s*-\s*\d+)?", "role"),
]

ROLE_PATTERNS = [
    r"\b(?:[Ss]enior|[Jj]unior)?\s*(?:[Dd]eveloper|[Dd]ata|[Ss]oftware|[Pp]roduct|[Mm]arketing|[Ss]ales|[Ee]ngineering|[Hh]R|[Oo]perations|[Ff]ull[- ]?[Ss]tack|[Ss]upport|[Ss]olution)\s+\w+(?:\s+\w+)?",
    r"\b(?:Backend Engineer|Frontend Engineer|Site Reliability Engineer I|Technical Solution Engineer)\b"
]

