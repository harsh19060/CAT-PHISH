"""Bounded HTTP status check for a public URL, without reading page content.

Redirects are deliberately not followed. DNS results are checked to reject
private, loopback, link-local, and otherwise non-public destinations.
"""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit

import requests


def check_url_reachability(url: str, timeout=(3.05, 5.0)) -> dict:
    """Return the first HTTP response status for a public HTTP(S) URL.

    A status such as 404 is returned as a response (it is not treated as proof
    of phishing). The streamed response is closed without consuming its body.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Enter a URL before checking reachability.")
    value = url.strip()
    candidate = value if "://" in value else f"https://{value}"
    try:
        parsed = urlsplit(candidate)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("The URL has an invalid host or port.") from exc
    if parsed.scheme.lower() not in {"http", "https"} or not host:
        raise ValueError("Only public HTTP or HTTPS URLs can be checked.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs containing embedded usernames or passwords cannot be checked.")

    effective_port = port or (443 if parsed.scheme.lower() == "https" else 80)
    try:
        literal = ipaddress.ip_address(host)
        resolved_addresses = [literal]
    except ValueError:
        try:
            records = socket.getaddrinfo(host, effective_port, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ConnectionError(f"Hostname could not be resolved: {exc}") from exc
        resolved_addresses = []
        for record in records:
            address_text = record[4][0].split("%", 1)[0]
            address = ipaddress.ip_address(address_text)
            if address not in resolved_addresses:
                resolved_addresses.append(address)
    if not resolved_addresses:
        raise ConnectionError("Hostname did not resolve to an IP address.")
    if any(not address.is_global for address in resolved_addresses):
        raise ValueError("For safety, reachability checks are limited to public internet hosts.")

    # Keep the query and path, remove fragments (which are never sent to servers).
    target = urlunsplit((parsed.scheme.lower(), parsed.netloc, parsed.path or "/", parsed.query, ""))
    try:
        response = requests.get(
            target,
            stream=True,
            allow_redirects=False,
            timeout=timeout,
            headers={"User-Agent": "PhishingURL-Lab/1.0"},
        )
    except requests.RequestException as exc:
        raise ConnectionError(f"Could not connect to the host: {exc}") from exc
    try:
        return {
            "status_code": int(response.status_code),
            "reason": str(response.reason or ""),
            "checked_url": target,
            "redirect_location": response.headers.get("Location") if 300 <= response.status_code < 400 else None,
        }
    finally:
        response.close()
