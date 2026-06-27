#!/usr/bin/env python3
"""Apify-compatible entrypoint for the public job-board change monitor."""

from __future__ import annotations

import json
import os
import sys
import asyncio
from pathlib import Path
from typing import Any

from job_board_monitor import run_actor

try:
    from apify import Actor
except ImportError:  # Local tests do not require the Apify SDK.
    Actor = None  # type: ignore[assignment]


def flatten_records(result: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for page in result["pages"]:
        source_url = page["source_url"]
        for job in page["jobs"]:
            records.append({"record_type": "job", "source_url": source_url, **job})
        for change in page["changes"]:
            records.append({"record_type": "change", "source_url": source_url, **change})
    return records


def write_jsonl(records_path: Path, records: list[dict[str, Any]]) -> None:
    records_path.parent.mkdir(parents=True, exist_ok=True)
    with records_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def run_local(input_path: Path, records_path: Path) -> int:
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        result = run_actor(payload)
        write_jsonl(records_path, flatten_records(result))
    except Exception as exc:
        print(f"public-job-board-change-monitor error: {exc}", file=sys.stderr)
        return 1
    return 0


def default_storage_paths() -> tuple[Path, Path]:
    input_path = Path(os.environ.get("APIFY_INPUT_PATH", "samples/input.json"))
    records_path = Path(os.environ.get("APIFY_OUTPUT_RECORDS_PATH", "storage/datasets/default/records.jsonl"))
    return input_path, records_path


async def run_apify() -> int:
    if Actor is None:
        return 1

    try:
        async with Actor:
            payload = await Actor.get_input() or {}
            result = run_actor(payload)
            for record in flatten_records(result):
                await Actor.push_data(record)
            await Actor.set_value("OUTPUT", result)
    except Exception as exc:
        print(f"public-job-board-change-monitor error: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    if Actor is not None and os.environ.get("APIFY_TOKEN"):
        return asyncio.run(run_apify())

    input_path, records_path = default_storage_paths()
    return run_local(input_path, records_path)


if __name__ == "__main__":
    raise SystemExit(main())
