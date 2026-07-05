from unittest.mock import patch

from src.scanner import scan_domain


@patch("src.scanner.is_live")
@patch("src.scanner.resolves")
def test_scan_skips_non_resolving(mock_resolves, mock_is_live):
    # Every candidate "doesn't resolve" → nothing should come back.
    mock_resolves.return_value = False
    results = scan_domain("paypal.com")
    assert results == []
    # is_live must never be called if nothing resolves (the funnel!)
    mock_is_live.assert_not_called()


@patch("src.scanner.is_live")
@patch("src.scanner.resolves")
def test_scan_returns_scored_sorted_results(mock_resolves, mock_is_live):
    # Everything resolves and is live → every candidate scores 7.
    mock_resolves.return_value = True
    mock_is_live.return_value = True

    results = scan_domain("paypal.com")

    assert len(results) > 0
    # All max score, and each result is a JSON-friendly dict.
    for r in results:
        assert r["score"] == 7
        assert r["resolves"] is True
        assert r["live"] is True
        assert isinstance(r["reasons"], list)
    # Sorted highest-first (all equal here, but the contract holds).
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)