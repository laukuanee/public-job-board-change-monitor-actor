# Product Brief

## Utility

Public Job Board Change Monitor Actor

## Problem

Operators, job seekers, recruiters, analysts, and market watchers often need to know when a public career page adds or removes roles. Vendor-specific scrapers are brittle, and generic page monitors usually return noisy HTML diffs instead of job-level change records.

## MVP

An Apify-ready actor that:

- accepts public career page URLs;
- optionally accepts saved HTML for controlled runs;
- extracts likely job listing links;
- normalizes absolute URLs and stable signatures;
- compares current listings to previous job records;
- emits `new`, `unchanged`, and `removed` changes.

## Buyer

- Job seekers monitoring target companies.
- Recruiting operations teams tracking competitor hiring.
- Market researchers watching hiring signals.
- Automation builders who need job-level diffs instead of page-level diffs.

## Monetization

Primary: Apify paid Actor usage.

Secondary: package into a broader monitoring toolkit after Apify publishing is available.

## Support Boundary

Support covers product-file usage, input/output format questions, and reproducible bugs. It does not include private account access, custom scraping evasion, login-only sites, CAPTCHAs, blocked data centers, or legal/compliance advice.
