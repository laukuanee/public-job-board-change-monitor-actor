#!/usr/bin/env python3
"""Extract and diff public job-board listings from career pages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen


JOB_HINTS = (
    "job",
    "jobs",
    "career",
    "careers",
    "position",
    "opening",
    "vacancy",
    "role",
    "greenhouse",
    "lever",
    "workday",
    "ashby",
    "recruitee",
    "data-job",
)

EXCLUDE_HINTS = (
    "about",
    "privacy",
    "terms",
    "cookie",
    "login",
    "sign-in",
    "signin",
    "benefits",
    "culture",
)


class JobLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self._active_link: dict[str, str] | None = None
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attributes = {key.lower(): value or "" for key, value in attrs}
        href = attributes.get("href", "")
        if not href:
            return
        self._active_link = {
            "url": href,
            "class": attributes.get("class", ""),
            "id": attributes.get("id", ""),
            "attrs": " ".join(f"{key}={value}" for key, value in attributes.items()),
        }
        self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._active_link is not None:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._active_link is not None:
            link = dict(self._active_link)
            link["text"] = clean_text(" ".join(self._text_parts))
            self.links.append(link)
            self._active_link = None
            self._text_parts = []


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def absolute_url(base_url: str, href: str) -> str:
    return urljoin(base_url, href)


def looks_like_public_job_link(link: dict[str, str]) -> bool:
    haystack = " ".join([link.get("url", ""), link.get("text", ""), link.get("class", ""), link.get("id", ""), link.get("attrs", "")]).lower()
    if any(excluded in haystack for excluded in EXCLUDE_HINTS):
        return False
    return any(hint in haystack for hint in JOB_HINTS)


def build_signature(title: str, url: str) -> str:
    return f"{slugify(title)}|{url}"


def dedupe_jobs(jobs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    duplicates = 0
    for job in jobs:
        key = job["url"]
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        deduped.append(job)
    return deduped, duplicates


def extract_jobs_from_html(source_url: str, html: str) -> dict[str, Any]:
    parser = JobLinkParser()
    parser.feed(html)

    candidates: list[dict[str, Any]] = []
    for link in parser.links:
        if not looks_like_public_job_link(link):
            continue
        url = absolute_url(source_url, link["url"])
        title = clean_text(link["text"]) or url
        candidates.append(
            {
                "title": title,
                "url": url,
                "signature": build_signature(title, url),
            }
        )

    jobs, duplicate_jobs = dedupe_jobs(candidates)
    return {
        "source_url": source_url,
        "jobs": jobs,
        "stats": {
            "links_seen": len(parser.links),
            "jobs_found": len(jobs),
            "duplicate_jobs_removed": duplicate_jobs,
        },
    }


def signature_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapped: dict[str, dict[str, Any]] = {}
    for row in rows:
        signature = row.get("signature")
        if not signature and row.get("title") and row.get("url"):
            signature = build_signature(str(row["title"]), str(row["url"]))
        if isinstance(signature, str):
            mapped[signature] = {**row, "signature": signature}
    return mapped


def compare_jobs(current_jobs: list[dict[str, Any]], previous_jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current = signature_map(current_jobs)
    previous = signature_map(previous_jobs)

    changes: list[dict[str, Any]] = []
    for signature, job in current.items():
        if signature not in previous:
            changes.append({"change_type": "new", **job})
    for signature, job in current.items():
        if signature in previous:
            changes.append({"change_type": "unchanged", **job})
    for signature, job in previous.items():
        if signature not in current:
            changes.append({"change_type": "removed", **job})
    return changes


def fetch_public_page(url: str, timeout_seconds: int = 10, max_bytes: int = 1_000_000) -> str:
    request = Request(url, headers={"User-Agent": "UtilityToUsageJobBoardMonitor/0.1 (+public job monitoring)"})
    with urlopen(request, timeout=timeout_seconds) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            raise ValueError(f"Unsupported content type for {url}: {content_type or 'unknown'}")
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"Page exceeds {max_bytes} byte limit: {url}")
    return data.decode("utf-8", errors="replace")


def run_actor(payload: dict[str, Any]) -> dict[str, Any]:
    pages = payload.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("Input must include a non-empty pages array")

    results: list[dict[str, Any]] = []
    for page in pages:
        if not isinstance(page, dict) or not isinstance(page.get("url"), str):
            raise ValueError("Each page must include a url")
        url = page["url"]
        html = page.get("html")
        if html is None:
            html = fetch_public_page(url)
        if not isinstance(html, str):
            raise ValueError(f"Page html must be text for {url}")
        previous_jobs = page.get("previous_jobs", payload.get("previous_jobs", []))
        if not isinstance(previous_jobs, list):
            raise ValueError(f"previous_jobs must be an array for {url}")
        page_result = extract_jobs_from_html(url, html)
        page_result["changes"] = compare_jobs(page_result["jobs"], previous_jobs)
        results.append(page_result)

    return {
        "page_count": len(results),
        "total_jobs": sum(len(page["jobs"]) for page in results),
        "total_changes": sum(len(page["changes"]) for page in results),
        "pages": results,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Actor-style JSON input file")
    parser.add_argument("--out", required=True, help="Output JSON path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = run_actor(payload)
    except Exception as exc:
        print(f"public-job-board-monitor error: {exc}", file=sys.stderr)
        return 1

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
