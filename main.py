import sys
from datetime import datetime, timezone

import yaml

from src.matcher import BrandMatcher
from src.stream import start_stream


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_watch(matcher: BrandMatcher):
    stats = {"seen": 0, "matched": 0}

    def on_domain(domain: str):
        stats["seen"] += 1

        # Heartbeat: proof of life without flooding the terminal
        if stats["seen"] % 1000 == 0:
            print(f"[stats] domains seen: {stats['seen']:,} | "
                  f"matches: {stats['matched']}")

        result = matcher.match(domain)
        if result:
            stats["matched"] += 1
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            line = (f"{ts} | {result.brand} | {result.match_type} | "
                    f"{result.domain} | {result.detail}")
            print(f"🚨 {line}")
            with open("matches.log", "a", encoding="utf-8") as f:
                f.write(line + "\n")

    print("Connecting to Certificate Transparency stream... (Ctrl+C to stop)")
    start_stream(on_domain)


if __name__ == "__main__":
    config = load_config()
    matcher = BrandMatcher(config["brands"])
    print(f"Loaded {len(config['brands'])} brands.")

    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        run_watch(matcher)
    elif len(sys.argv) > 1:
        result = matcher.match(sys.argv[1])
        if result:
            print(f"🚨 MATCH: {result.detail} (type: {result.match_type})")
        else:
            print("✅ No match.")