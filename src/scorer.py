"""Risk scoring for matched domains.

Turns a Match + enrichment signals into a single score so that
alerting can apply a threshold. Weights are hand-tuned guesses
for now — refining them against real observations is the point
of running this thing.
"""

from dataclasses import dataclass

from src.matcher import Match


@dataclass
class ScoredMatch:
    match: Match
    resolves: bool
    live: bool
    score: int
    reasons: list[str]


def score_match(match: Match, resolves: bool, live: bool) -> ScoredMatch:
    score = 0
    reasons = []

    if match.match_type == "permutation":
        score += 3
        reasons.append("known typo/homoglyph permutation (+3)")
    else:  # keyword
        score += 1
        reasons.append("brand keyword in domain (+1)")

    if resolves:
        score += 2
        reasons.append("domain resolves in DNS (+2)")

    if live:
        score += 2
        reasons.append("live web server responding (+2)")

    return ScoredMatch(match=match, resolves=resolves,
                       live=live, score=score, reasons=reasons)