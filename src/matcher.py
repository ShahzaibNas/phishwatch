"""Brand matching engine for PhishWatch.

Given a set of protected brands, decides whether an arbitrary
domain looks like an impersonation attempt — and explains why.
"""

from dataclasses import dataclass

import tldextract
from dnstwist import Fuzzer


@dataclass
class Match:
    """A positive detection, with evidence for later scoring."""
    domain: str       # the suspicious domain we checked
    brand: str        # which protected brand it resembles
    match_type: str   # "permutation" or "keyword"
    detail: str       # human-readable reason


def normalize(domain: str) -> str:
    """Clean raw domain strings from CT logs.

    CT entries arrive messy: mixed case, trailing dots,
    wildcard prefixes like '*.example.com'.
    """
    d = domain.strip().lower().rstrip(".")
    if d.startswith("*."):
        d = d[2:]
    return d


def registered_domain(domain: str) -> str:
    """'login.safepay.co.uk' -> 'safepay.co.uk'."""
    ext = tldextract.extract(domain)
    return ext.top_domain_under_public_suffix or domain


def generate_permutations(domain: str) -> set[str]:
    """All typo/homoglyph/TLD-swap permutations of a brand domain.

    Uses dnstwist's Fuzzer WITHOUT DNS resolution — pure string
    generation, so it's fast and runs offline.
    """
    fuzzer = Fuzzer(domain)
    fuzzer.generate()
    return {p["domain"] for p in fuzzer.domains}


class BrandMatcher:
    """Precomputes permutation sets once; per-domain checks are O(1)."""

    MIN_KEYWORD_LEN = 5  # 'hub' in a domain means nothing; 'safepay' does

    def __init__(self, brands: list[dict]):
        self.brands = brands
        self._permutations: dict[str, set[str]] = {
            b["name"]: generate_permutations(b["domain"]) for b in brands
        }

    def match(self, raw_domain: str) -> Match | None:
        d = normalize(raw_domain)
        reg = registered_domain(d)

        for b in self.brands:
            name = b["name"].lower()
            own = b["domain"].lower()

            # Never flag the brand itself or its real subdomains.
            if d == own or d.endswith("." + own):
                return None

            # 1. Strongest signal: known typo/homoglyph permutation.
            if reg in self._permutations[b["name"]]:
                return Match(d, b["name"], "permutation",
                             f"'{reg}' is a known permutation of {own}")

            # 2. Weaker signal: brand name embedded in the domain,
            #    e.g. safepay-verify.com, login-safepay.net
            if len(name) >= self.MIN_KEYWORD_LEN and name in d:
                return Match(d, b["name"], "keyword",
                             f"domain contains brand name '{name}'")

        return None