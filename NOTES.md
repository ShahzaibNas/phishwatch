# Field Notes

## Week 2 — first live runs
- Same domain alerted twice (paypal-danmark.creditunion.ca) → CT logs
  emit precerts + certs and multiple logs → dedup is required
- Free subdomain services (nut.cc) are a recurring phishing pattern
- Keyword matches are common but noisy; permutation matches rare but strong
- Calidog public certstream is dead → self-hosted certstream-server-go
  locally; only stream.py's URL changed (separation of concerns win)

## Week 3 — scoring and alerts
- ww16.ww16.ww16.paypal-bre.wery.com: stacked junk subdomains + brand
  bait; scored 5 (keyword+resolves+live); dedup on registered domain
  collapses all its siblings
- Enrichment only runs on matches (~3 per 250k domains) — funnel works
- Known future improvement: matches should go to a queue/worker instead
  of enriching inside the stream callback