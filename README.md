# Public Job Board Change Monitor Actor

Status: local MVP ready for Apify packaging review.

This Apify-style actor extracts likely job listing links from public career pages and compares them against a previous job snapshot. It emits normalized job records plus `new`, `unchanged`, and `removed` change records.

## Safe Use Boundary

- Public career pages and public job board result pages only.
- No account login, private workspace access, CAPTCHA handling, MFA, or evasion.
- No hidden API abuse or high-frequency polling.
- Buyers are responsible for using it only where public monitoring is allowed.

## Input

```json
{
  "pages": [
    {
      "url": "https://example.com/jobs",
      "previous_jobs": [
        {
          "title": "Data Engineer",
          "url": "https://example.com/jobs/data-engineer",
          "signature": "data-engineer|https://example.com/jobs/data-engineer"
        }
      ]
    }
  ]
}
```

For offline demos or controlled tests, each page can include an `html` string.

## Output

The local CLI returns a summary object:

- `pages[].jobs`: current normalized job listings.
- `pages[].changes`: change records with `change_type` of `new`, `unchanged`, or `removed`.
- `pages[].stats`: link count and dedupe stats.

The Apify-compatible `main.py` writes JSONL dataset records with `record_type` of `job` or `change`.

## Local Commands

```powershell
C:\Users\lauku\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s tests -v
C:\Users\lauku\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\job_board_monitor.py --input .\samples\input.json --out .\samples\output.json
C:\Users\lauku\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\main.py
```

## Differentiator

Most basic job scrapers focus on one vendor or only dump listings. This actor is deliberately generic for public pages and change-oriented: it returns stable signatures and removed-listing detection so it can feed alerts, applicant tracking research, or market monitoring workflows without private account access.
