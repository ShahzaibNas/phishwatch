import pytest

from src.matcher import BrandMatcher, normalize, registered_domain

BRANDS = [{"name": "safepay", "domain": "safepay.pk"}]


@pytest.fixture(scope="module")
def matcher():
    # scope="module": build the matcher ONCE and reuse it for all
    # tests below. Permutation generation is the slow part — no
    # need to redo it for every single test.
    return BrandMatcher(BRANDS)


def test_normalize_handles_ct_log_mess():
    assert normalize("  *.SafePay.PK.  ") == "safepay.pk"


def test_registered_domain_multi_part_tld():
    assert registered_domain("login.safepay.co.uk") == "safepay.co.uk"


def test_own_domain_never_flagged(matcher):
    assert matcher.match("safepay.pk") is None


def test_own_subdomain_never_flagged(matcher):
    assert matcher.match("login.safepay.pk") is None


def test_keyword_hit(matcher):
    m = matcher.match("safepay-verify.com")
    assert m is not None
    assert m.brand == "safepay"
    assert m.match_type == "keyword"


def test_permutation_hit(matcher):
    # Pick a real permutation from the generated set, so the test
    # is deterministic no matter what dnstwist generates.
    perm = next(iter(matcher._permutations["safepay"] - {"safepay.pk"}))
    m = matcher.match(perm)
    assert m is not None
    assert m.match_type in ("permutation", "keyword")


def test_unrelated_domain_ignored(matcher):
    assert matcher.match("google.com") is None
    assert matcher.match("nytimes.com") is None