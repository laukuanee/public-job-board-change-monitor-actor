# Apify Listing Draft

## Title

Public Job Board Change Monitor

## Short Description

Monitor public career pages for job-level additions and removals without logging in or scraping private accounts.

## Description

Public Job Board Change Monitor extracts likely job listing links from public career pages and compares them against a previous snapshot. It returns normalized job records plus `new`, `unchanged`, and `removed` change records that can feed alerts, dashboards, applicant research, or hiring-signal workflows.

The actor is designed for public pages only. It does not log in, bypass bot checks, solve CAPTCHAs, or access private applicant tracking systems.

## Use Cases

- Track target-company openings as a job seeker.
- Watch competitor hiring changes.
- Build weekly hiring-signal reports.
- Feed public job changes into Slack, email, Airtable, or a dashboard.

## Output Fields

- `record_type`: `job` or `change`.
- `source_url`: monitored page URL.
- `title`: normalized job title text.
- `url`: absolute job posting URL.
- `signature`: stable title+URL signature for future comparisons.
- `change_type`: `new`, `unchanged`, or `removed` for change records.

## Pricing Draft

Launch as a usage-based Apify Actor with `Try for free` enabled and the lowest available paid usage tier in the Store UI/API. Keep this priced as a public-page monitoring helper, not a recruiting-data platform.

Keep a free local/demo sample in the README. Raise pricing only after there are repeated runs, saved tasks, or review signals.

## Safety Notes

Use this actor only on public pages where monitoring is permitted. Do not use it for login-only content, private job boards, CAPTCHAs, or anti-bot evasion.
