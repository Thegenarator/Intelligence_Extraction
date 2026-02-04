import re
from typing import Dict, List


ACCOUNT_RE = re.compile(r"\b\d{8,18}\b")
IFSC_RE = re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", re.IGNORECASE)
UPI_RE = re.compile(r"\b[A-Za-z0-9.\-_]{2,}@\w+\b")
URL_RE = re.compile(r"(https?://[^\s]+)", re.IGNORECASE)
AMOUNT_RE = re.compile(r"\b(?:inr|rs\.?|rupees|usd|\$)\s?\d{2,7}\b", re.IGNORECASE)


def _clean_url(url: str) -> str:
    return url.rstrip(".,);]").strip()


def extract_intel(text: str) -> Dict[str, List[Dict]]:
    """
    Regex-first extraction with light normalization and confidence tagging.
    """
    bank_accounts = [{"value": m, "confidence": 0.78} for m in ACCOUNT_RE.findall(text)]
    upi_ids = [{"value": m.lower(), "confidence": 0.8} for m in UPI_RE.findall(text)]
    urls = [{"value": _clean_url(m), "confidence": 0.75} for m in URL_RE.findall(text)]
    amounts = [{"value": m, "confidence": 0.4} for m in AMOUNT_RE.findall(text)]

    ifsc_codes = [code.upper() for code in IFSC_RE.findall(text)]
    if bank_accounts and ifsc_codes:
        for i, acct in enumerate(bank_accounts):
            bank_accounts[i] = {**acct, "ifsc": ifsc_codes[min(i, len(ifsc_codes) - 1)]}

    return {
        "bank_accounts": bank_accounts,
        "upi_ids": upi_ids,
        "urls": urls,
        "amounts": amounts,
    }

