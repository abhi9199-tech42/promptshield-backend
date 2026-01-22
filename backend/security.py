import re
from typing import Tuple

# Common PII Regex Patterns
EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_REGEX = r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b'
CREDIT_CARD_REGEX = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
SSN_REGEX = r'\b\d{3}-\d{2}-\d{4}\b'

def scrub_pii(text: str) -> Tuple[str, bool]:
    """
    Scrub PII from text using regex patterns.
    Returns:
        Tuple[str, bool]: (scrubbed_text, found_pii)
    """
    scrubbed_text = text
    found_pii = False

    # Scrub Emails
    if re.search(EMAIL_REGEX, scrubbed_text):
        scrubbed_text = re.sub(EMAIL_REGEX, '<EMAIL_REDACTED>', scrubbed_text)
        found_pii = True

    # Scrub Phone Numbers
    if re.search(PHONE_REGEX, scrubbed_text):
        scrubbed_text = re.sub(PHONE_REGEX, '<PHONE_REDACTED>', scrubbed_text)
        found_pii = True

    # Scrub Credit Cards
    if re.search(CREDIT_CARD_REGEX, scrubbed_text):
        scrubbed_text = re.sub(CREDIT_CARD_REGEX, '<CC_REDACTED>', scrubbed_text)
        found_pii = True
        
    # Scrub SSN
    if re.search(SSN_REGEX, scrubbed_text):
        scrubbed_text = re.sub(SSN_REGEX, '<SSN_REDACTED>', scrubbed_text)
        found_pii = True

    return scrubbed_text, found_pii
