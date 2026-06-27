# Publish Checklist

- [x] Local engine exists.
- [x] Tests cover extraction, dedupe, diffing, input validation, schema, and JSONL entrypoint.
- [x] Sample input and output exist.
- [x] Apify metadata exists: `apify.json`, `INPUT_SCHEMA.json`, `Dockerfile`, `main.py`.
- [x] Listing draft exists.
- [x] Safety boundary is documented.
- [ ] Apify account publishing path verified without hard-stop prompts.
- [ ] Apify creator payout/monetization setup verified by user if prompted.
- [ ] Publish actor to Apify Store.
- [ ] Add live actor URL to `UTILITY_USAGE_LOG.md`.

## Current Blocker

Actual Apify marketplace publishing may require account/session, terms, payout, billing, identity, or security prompts. Stop before those hard-stop prompts and keep the local product ready.
