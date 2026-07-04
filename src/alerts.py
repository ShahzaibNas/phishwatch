"""Alert delivery for PhishWatch."""

import requests

from src.scorer import ScoredMatch


def format_alert(sm: ScoredMatch) -> str:
    lines = [
        f"🚨 **PhishWatch alert** — score {sm.score}",
        f"Domain: `{sm.match.domain}`",
        f"Brand: {sm.match.brand}",
        f"Type: {sm.match.match_type}",
        "Signals: " + "; ".join(sm.reasons),
    ]
    return "\n".join(lines)


def send_webhook(sm: ScoredMatch, config: dict) -> bool:
    text = format_alert(sm)
    alerts_cfg = config.get("alerts", {})

    url = alerts_cfg.get("discord_webhook") or ""
    if url:
        payload = {"content": text}
    else:
        url = alerts_cfg.get("slack_webhook") or ""
        payload = {"text": text}

    if not url:
        return False

    try:
        requests.post(url, json=payload, timeout=5)
        return True
    except requests.RequestException:
        return False