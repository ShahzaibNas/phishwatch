"""Enrichment checks for matched domains.

These are SLOW (network calls) — only ever run on matches,
never on the raw stream.
"""

import socket

import requests


def resolves(domain: str) -> bool:
    """True if the domain has at least one DNS A/AAAA record."""
    try:
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False
    except Exception:
        return False


def is_live(domain: str, timeout: float = 5.0) -> bool:
    """True if an HTTP(S) server answers on the domain.

    We try https first, then http. Any status code counts as
    'live' — even a 403 or 404 means a server is there.
    """
    for scheme in ("https", "http"):
        try:
            requests.get(f"{scheme}://{domain}", timeout=timeout,
                         allow_redirects=True)
            return True
        except requests.RequestException:
            continue
    return False