"""URL-string features shared by training and live inference.

The first five correspond to selected PhiUSIIL fields; the additional fields
have explicit project definitions and are also computed from each raw URL.
Reachability checking is handled separately by ``src.url_check``.
"""
from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

import pandas as pd

SOURCE_FEATURE_NAMES = ["URLLength", "DomainLength", "IsDomainIP", "TLDLength", "NoOfSubDomain"]
FEATURE_NAMES = [
    *SOURCE_FEATURE_NAMES,
    "IsHTTPS",
    "NoOfLettersInURL",
    "NoOfDigitsInURL",
    "NoOfAtSymbols",
    "HasPercentEncoding",
    "LetterRatioInURL",
    "DigitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQuestionMarksInURL",
    "NoOfAmpersandsInURL",
    "NoOfDotsInURL",
    "NoOfHyphensInURL",
    "NoOfSlashesInURL",
    "NoOfNonAlphanumericCharsInURL",
    "NonAlphanumericRatioInURL",
    "PathLength",
    "QueryLength",
    "QueryParameterCount",
    "NoOfPercentEncodings",
    "PercentEncodedRatioInURL",
]


def _parse_url(value: str):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Enter a non-empty URL.")
    value = value.strip()
    # Match the reachability check's default when a user enters a bare host.
    candidate = value if "://" in value else f"https://{value}"
    try:
        parsed = urlsplit(candidate)
        host = parsed.hostname
        port = parsed.port  # Access validates non-numeric and out-of-range ports.
    except ValueError as exc:
        raise ValueError("The URL could not be parsed. Check its format.") from exc
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Enter an HTTP or HTTPS web URL.")
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("The URL port must be between 1 and 65535.")
    labels = host.rstrip(".").split(".") if host else []
    if (not host or "." not in host or any(not label for label in labels)
            or any(ch.isspace() for ch in value)):
        raise ValueError("Enter a URL with a hostname, such as https://example.com.")
    return candidate, parsed, host.rstrip(".").lower()


def extract_url_features(url: str, *, as_frame: bool = True):
    """Extract the fixed feature vector, optionally as a one-row DataFrame.

    Training requests a compact list to keep full-corpus extraction efficient;
    the app uses the default DataFrame form to preserve column names and order.
    Both paths use this same parser and feature calculation.
    """
    value, parsed, host = _parse_url(url)
    try:
        ipaddress.ip_address(host.strip("[]"))
        is_ip = 1
    except ValueError:
        is_ip = 0
    labels = [part for part in host.split(".") if part]
    # An IPv4 host is not a hierarchy of domain labels.
    if is_ip:
        labels = []
        subdomains = 0
    else:
        # NoOfSubDomain counts hostname labels before the final two labels.
        subdomains = max(0, len(labels) - 2)
    letters = sum(char.isalpha() for char in value)
    digits = sum(char.isdigit() for char in value)
    percent_encodings = len(re.findall(r"%[0-9a-fA-F]{2}", value))
    non_alphanumeric = len(re.findall(r"[^A-Za-z0-9]", value))
    url_length = len(value)
    values = [
        url_length, len(host), is_ip,
        len(labels[-1]) if labels else 0, subdomains,
        int(parsed.scheme.lower() == "https"), letters, digits,
        value.count("@"), int(percent_encodings > 0),
        letters / url_length, digits / url_length,
        value.count("="), value.count("?"), value.count("&"),
        value.count("."), value.count("-"), value.count("/"),
        non_alphanumeric, non_alphanumeric / url_length,
        len(parsed.path), len(parsed.query),
        0 if not parsed.query else parsed.query.count("&") + 1,
        percent_encodings, percent_encodings / url_length,
    ]
    if not as_frame:
        return values
    return pd.DataFrame([values], columns=FEATURE_NAMES)
