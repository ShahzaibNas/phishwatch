"""One-shot scan engine for PhishWatch.

Given a domain, generate lookalike permutations, check which ones
actually exist (resolve + serve content), score them, and return
a sorted report. Reuses enrich and scorer — the same building
blocks as the stream watcher, assembled for request-response.

NOTE: capped at MAX_PERMUTATIONS to keep a live scan responsive.
This trades exhaustiveness for speed — a deliberate MVP choice.
"""

from dataclasses import dataclass, asdict

from dnstwist import Fuzzer

from src.matcher import Match, normalize
from src.enrich import resolves, is_live
from src.scorer import score_match


MAX_PERMUTATIONS = 40  # cap so a scan stays under ~60s


@dataclass
class ScanResult:
    domain: str
    score: int
    resolves: bool
    live: bool
    reasons: list[str]


def scan_domain(target: str) -> list[dict]:
    """Scan a domain for live lookalikes. Returns a list of dicts
    (JSON-friendly) sorted by score, highest first."""
    target = normalize(target)

    # Generate permutations, then cap. dnstwist's first results are
    # the higher-signal transforms (typos, homoglyphs), so taking
    # the first N is a reasonable filter.
    fuzzer = Fuzzer(target)
    fuzzer.generate()
    candidates = [p["domain"] for p in fuzzer.domains
                  if p["domain"] != target][:MAX_PERMUTATIONS]

    results: list[ScanResult] = []
    for cand in candidates:
        r = resolves(cand)
        if not r:
            continue  # skip dead permutations entirely
        live = is_live(cand)

        # Build a Match so we can reuse the scorer. These are
        # permutations by construction.
        m = Match(domain=cand, brand=target,
                  match_type="permutation",
                  detail=f"lookalike of {target}")
        sm = score_match(m, resolves=r, live=live)

        results.append(ScanResult(
            domain=cand, score=sm.score,
            resolves=r, live=live, reasons=sm.reasons,
        ))

    results.sort(key=lambda x: x.score, reverse=True)
    return [asdict(r) for r in results]