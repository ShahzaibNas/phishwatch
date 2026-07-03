import sys

import yaml

from src.matcher import BrandMatcher


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    config = load_config()
    matcher = BrandMatcher(config["brands"])
    print(f"Loaded {len(config['brands'])} brands.")

    if len(sys.argv) > 1:
        result = matcher.match(sys.argv[1])
        if result:
            print(f"🚨 MATCH: {result.detail} (type: {result.match_type})")
        else:
            print("✅ No match.")