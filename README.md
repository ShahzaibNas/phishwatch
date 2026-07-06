# PhishWatch

**Real-time detection of lookalike domains and brand impersonation, built on public Certificate Transparency logs.**

PhishWatch surfaces the typosquats, homograph attacks, and cloned-brand domains that attackers use to phish your customers — the moment their SSL certificates go live. It offers both an instant on-demand scan and continuous 24/7 monitoring, with risk-scored results.

## The Problem

Attackers register thousands of lookalike domains every day — `paypa1.com`, `xn--pypal-4ve.com`, `safepay-verify.net` — to clone login pages and steal credentials. Enterprise brand-protection tools (Bolster, Red Sift, PhishLabs) detect these well, but are priced for large security teams. Smaller companies are left exposed. PhishWatch brings the core capability within reach.

## Features

- **One-time scan** — enter a domain, get a risk-scored report of live lookalikes in under a minute
- **Continuous monitoring** — watch the Certificate Transparency stream 24/7 for your brands, with alerts to Discord/Slack
- **Detection engine** — typo, homograph, and keyword permutation matching via dnstwist
- **Live verification** — DNS resolution and web-server liveness checks, so results are evidence not guesses
- **7-point risk scoring** — combines pattern strength with whether a lookalike is actually live
- **Web dashboard** — five-page interface with scan, monitoring, and brand management
- **Abuse protection** — rate limiting and input validation on all endpoints

## Architecture

PhishWatch is built as decoupled components that share a database. The stream watcher and the web app never talk directly — the database is their meeting point, which keeps each component independently testable and replaceable.

## Tech Stack

Python · FastAPI · SQLModel · dnstwist · tldextract · Certificate Transparency (certstream) · pytest · vanilla JS/CSS frontend

## Getting Started

```bash
git clone https://github.com/ShahzaibNas/phishwatch
cd phishwatch
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
cp config.example.yaml config.yaml   # then add your webhook URL
```

### Run the web app (scan + dashboard)

```bash
python -m uvicorn api:app --reload
# open http://127.0.0.1:8000/
```

### Run continuous monitoring

Requires a local certstream-server-go instance running (the public Calidog server is no longer reliable — see NOTES.md).

```bash
python main.py watch
```

## Testing

```bash
python -m pytest tests/ -v
```

## Project Structure

## Roadmap

- [x] Brand permutation & matching engine
- [x] Certificate Transparency stream ingestion
- [x] DNS / liveness enrichment
- [x] Risk scoring & Discord alerts
- [x] One-time scan web UI
- [x] Database-backed continuous monitoring
- [x] Five-page product site
- [ ] Production deployment (24/7)
- [ ] User accounts & multi-tenancy
- [ ] Automated takedown guidance

## Why I Built This

I'm a final-year computer science student interested in the intersection of security and automation. I built PhishWatch end to end — from a domain-matching engine to a live web product — to learn how real software is engineered and shipped, not just prototyped. It's developed in public, one component at a time.

## Notes

Built with a decoupled, test-driven approach. See NOTES.md for field observations and engineering decisions made along the way — including why the public certstream server was replaced with a self-hosted one, and how the false-positive funnel keeps alerts trustworthy.

## License

MIT