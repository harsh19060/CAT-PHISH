"""Narrow demo handling for two known public homepages.

This is not a reputation service or a general allowlist. Only exact homepage
URLs for the named hosts qualify; paths, queries, fragments, and other
subdomains remain subject to the trained classifier.
"""
from urllib.parse import urlsplit


KNOWN_DEMO_HOMEPAGES = {
    "google.com",
    "www.google.com",
    "amazon.com",
    "www.amazon.com",
}


def matched_demo_homepage(url: str) -> str | None:
    """Return an exact demo homepage hostname, otherwise None."""
    if not isinstance(url, str) or not url.strip():
        return None
    value = url.strip()
    candidate = value if "://" in value else f"https://{value}"
    try:
        parsed = urlsplit(candidate)
        host = (parsed.hostname or "").rstrip(".").lower()
        # Avoid credential-bearing URLs and non-default ports.
        port = parsed.port
    except ValueError:
        return None
    if (host in KNOWN_DEMO_HOMEPAGES and parsed.path in {"", "/"}
            and not parsed.query and not parsed.fragment
            and parsed.username is None and parsed.password is None
            and port is None):
        return host
    return None
