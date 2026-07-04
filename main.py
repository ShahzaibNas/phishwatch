from src.matcher import BrandMatcher, registered_domain
from src.enrich import resolves, is_live
from src.scorer import score_match
from src.alerts import send_webhook


import sys
from datetime import datetime, timezone

import yaml

from src.matcher import BrandMatcher
from src.stream import start_stream


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_watch(matcher: BrandMatcher, config: dict):
    stats = {"seen": 0, "matched": 0, "alerted": 0}
    alerted_domains: set[str] = set()   # dedup for this run
    min_score = config.get("alerts", {}).get("min_score", 4)

    def on_domain(domain: str):
        stats["seen"] += 1
        if stats["seen"] % 1000 == 0:
            print(f"[stats] seen: {stats['seen']:,} | "
                  f"matched: {stats['matched']} | "
                  f"alerted: {stats['alerted']}")

        result = matcher.match(domain)
        if not result:
            return
        stats["matched"] += 1

        # Dedup on the registered domain so www.x.com and x.com
        # count as one incident
        key = registered_domain(result.domain)
        if key in alerted_domains:
            return
        alerted_domains.add(key)

        # Enrichment — slow, but only runs on rare deduped matches
        r = resolves(result.domain)
        live = is_live(result.domain) if r else False
        sm = score_match(result, r, live)

        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        line = (f"{ts} | score={sm.score} | {result.brand} | "
                f"{result.match_type} | {result.domain} | "
                f"{'; '.join(sm.reasons)}")
        print(f"🚨 {line}")
        with open("matches.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")

        if sm.score >= min_score:
            if send_webhook(sm, config):
                stats["alerted"] += 1

    print("Connecting to Certificate Transparency stream... (Ctrl+C to stop)")
    start_stream(on_domain)


if __name__ == "__main__":
    config = load_config()
    matcher = BrandMatcher(config["brands"])
    print(f"Loaded {len(config['brands'])} brands.")

    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        run_watch(matcher, config)
    elif len(sys.argv) > 1:
        result = matcher.match(sys.argv[1])
        if result:
            print(f"🚨 MATCH: {result.detail} (type: {result.match_type})")
        else:
            print("✅ No match.")