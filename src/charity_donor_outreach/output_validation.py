from __future__ import annotations

import re
from decimal import Decimal
from urllib.parse import urlparse

from .claims import validate_claims
from .errors import OutputValidationError
from .models import CampaignClaim, LetterDraft

DANGEROUS_HTML = re.compile(r"<(script|iframe|object|embed)\b|\son[a-z]+\s*=", re.IGNORECASE)
PLACEHOLDER = re.compile(r"\{\{.*?\}\}|\[\s*[A-Z][A-Z _-]+\s*\]")
URL = re.compile(r"https?://[^\s<\"']+")
PIXEL = re.compile(r"<img\b[^>]*(?:width=[\"']?1|height=[\"']?1)", re.IGNORECASE)


def validate_output(
    letter: LetterDraft,
    *,
    ask: Decimal,
    donation_url: str,
    claims: list[CampaignClaim],
    claim_policy: dict[str, object],
) -> None:
    combined = "\n".join((letter.subject, letter.html, letter.plain_text))
    if DANGEROUS_HTML.search(letter.html) or PIXEL.search(letter.html):
        raise OutputValidationError("unsafe HTML element, event handler, or tracking pixel")
    if PLACEHOLDER.search(combined):
        raise OutputValidationError("unresolved template placeholder")
    expected = f"{ask:.2f}"
    if expected not in letter.html or expected not in letter.plain_text:
        raise OutputValidationError("approved ask is missing or changed")
    allowed = urlparse(donation_url)
    for raw_url in URL.findall(letter.html):
        candidate = urlparse(raw_url.rstrip(".").rstrip("'").rstrip(")"))
        if candidate.scheme != "https" or candidate.netloc != allowed.netloc:
            raise OutputValidationError(f"unauthorized URL: {raw_url}")
    validate_claims(combined, claims, claim_policy)
