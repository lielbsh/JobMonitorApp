BOOTSTRAP_QUERY = (
    '("application was sent" OR "application for" OR applied OR applying OR '
    '"application has been received" OR "thank you for applying" OR "received your CV" OR "submitting your resume" OR '
    '"thanks for your interest" OR "following the interview" OR "update regarding your application" OR '
    '"recruiting team" OR "job application") '
    '-subject:(newsletter OR promotion OR "get started" OR reset OR verify) '
    'newer_than:60d ' # adjust as needed
)

RUN_QUERY_TEMPLATE = (
    'after:{timestamp} '
    '("application was sent" OR "application for" OR applied OR applying OR "your application to" OR '
    '"application has been received" OR "received your CV" OR "submitting your resume" OR '
    '"thanks for your interest" OR "interview" OR "job application" OR '
    '"recruiting team" OR "hr team" OR "Talent Acquisition Team") '
    '-subject:(newsletter OR promotion OR "get started" OR reset OR verify) '
)
