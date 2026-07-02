# PhishWatch

Real time detection of phishing and brand impersonation domains.

## The Problem

Every day, attackers register thousands of deceptive domains designed to impersonate legitimate brands. Domains such as paypa1.com, micr0soft-login.com, and secure-paypal-verify.net are commonly used to host fake login pages, steal credentials and launch phishing campaigns.

While enterprise grade brand protection platforms provide this capability, they are often too expensive for startups, small businesses, SaaS companies and digital agencies. As a result many organizations remain unaware of phishing domains targeting their brands until customers have already been affected.

## What This Does

PhishWatch continuously monitors newly issued SSL/TLS certificates through public Certificate Transparency (CT) logs to identify domains that resemble protected brands.

Using typo detection, homoglyph analysis and keyword based matching, the system identifies suspicious domains shortly after they are registered. Each detected domain is further analyzed through DNS and content checks, assigned a risk score and delivered as an alert via Slack, Discord, or email within minutes.

## Status

Early development.
Current roadmap:

- [ ] Brand permutation & matching engine
- [ ] Certificate Transparency stream ingestion
- [ ] DNS / liveness enrichment
- [ ] Scoring + alert delivery (Slack webhook)
- [ ] 24/7 deployment

## Why I'm Building This

I'm a Computer Science student with a strong interest in cybersecurity, automation and building practical security tools. I started PhishWatch to learn how production security systems work while creating something that can genuinely help startups and small businesses defend against phishing attacks. I'm building the project in public to improve my engineering skills and share the journey from idea to product.

## Tech
Python
Certificate Transparency (CT) Logs
dnstwist
DNS Resolution
Slack Webhooks
Discord Webhooks
GitHub Actions (planned)
Docker (planned)
FastAPI (planned)
