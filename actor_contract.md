# Actor Contract

## Input Schema

See `INPUT_SCHEMA.json`.

Required:

- `pages`: non-empty array.
- `pages[].url`: public career or job-board page URL.

Optional:

- `pages[].html`: saved HTML for offline testing.
- `pages[].previous_jobs`: prior job records with `title`, `url`, and `signature`.

## Job Record

```json
{
  "record_type": "job",
  "source_url": "https://example.com/jobs",
  "title": "Data Engineer",
  "url": "https://example.com/jobs/data-engineer",
  "signature": "data-engineer|https://example.com/jobs/data-engineer"
}
```

## Change Record

```json
{
  "record_type": "change",
  "source_url": "https://example.com/jobs",
  "change_type": "new",
  "title": "Product Manager",
  "url": "https://example.com/jobs/product-manager",
  "signature": "product-manager|https://example.com/jobs/product-manager"
}
```

## Errors

- Missing `pages`: `Input must include a non-empty pages array`.
- Missing page URL: `Each page must include a url`.
- Non-text HTML: `Page html must be text for <url>`.
- Unsupported fetched content type: `Unsupported content type for <url>`.
- Page too large: `Page exceeds <limit> byte limit`.

## Limits

Current MVP uses heuristic link extraction. It is best for career pages where listings are represented as links. It does not execute JavaScript, solve bot checks, or access private listings.
