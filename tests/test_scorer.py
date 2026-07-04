from src.matcher import Match
from src.scorer import score_match


def _fake_match(match_type: str) -> Match:
    """Helper: build a Match by hand so tests need no matcher,
    no config, and no network — just the scorer's arithmetic."""
    return Match(
        domain="paypa1-test.com",
        brand="paypal",
        match_type=match_type,
        detail="fabricated for testing",
    )


def test_permutation_resolving_live_scores_7():
    # Strongest possible signal combination: 3 + 2 + 2
    sm = score_match(_fake_match("permutation"), resolves=True, live=True)
    assert sm.score == 7


def test_keyword_alone_scores_1():
    # Weakest signal: keyword hit on a domain that doesn't even
    # resolve. Must stay far below any sane alert threshold.
    sm = score_match(_fake_match("keyword"), resolves=False, live=False)
    assert sm.score == 1


def test_keyword_resolving_live_scores_5():
    # The ww16-style case: keyword + resolves + live = 1 + 2 + 2.
    # This is exactly the alert you received in Discord.
    sm = score_match(_fake_match("keyword"), resolves=True, live=True)
    assert sm.score == 5


def test_reasons_are_always_populated():
    # Every score must be explainable — the reasons list is what
    # goes into the alert. An unexplained score is a bug.
    sm = score_match(_fake_match("permutation"), resolves=False, live=False)
    assert len(sm.reasons) > 0
    assert sm.score == 3