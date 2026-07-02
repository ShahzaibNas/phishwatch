import yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    brands = [b["name"] for b in config["brands"]]
    print(f"Monitoring {len(brands)} brands: {', '.join(brands)}")
