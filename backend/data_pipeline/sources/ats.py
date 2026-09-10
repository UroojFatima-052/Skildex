"""Live job postings from Greenhouse and Lever public APIs.

Runs in batches. Each run picks up where the last one stopped and
appends to the raw file, so batches accumulate instead of overwriting.
The cursor only advances after a batch completes, so an interrupted
run is retried rather than skipped.
"""

import html
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

from data_pipeline.config import (
    RAW_DIR,
    GREENHOUSE_COMPANIES_URL,
    LEVER_COMPANIES_URL,
)

SOURCE_NAME = "ats"
RAW_FILE = RAW_DIR / "ats.jsonl"
CURSOR_FILE = RAW_DIR / "ats_cursor.json"

GREENHOUSE_JOBS = "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true"
LEVER_JOBS = "https://api.lever.co/v0/postings/{}?mode=json"

WORKERS = 8
BATCH_SIZE = 500
TIMEOUT = 10
HEADERS = {"User-Agent": "SkildexBot/0.1 (+https://github.com/UroojFatima-052/skildex)"}


def _strip_html(text):
    text = html.unescape(str(text))
    return re.sub(r"<[^>]+>", " ", text)


def _read_cursor():
    if CURSOR_FILE.exists():
        return json.loads(CURSOR_FILE.read_text(encoding="utf-8"))
    return {}


def _write_cursor(cursor):
    CURSOR_FILE.write_text(json.dumps(cursor), encoding="utf-8")


def _next_batch(url, platform):
    """Return the next batch of slugs. Does NOT advance the cursor."""
    slugs = requests.get(url, timeout=TIMEOUT).json()

    cursor = _read_cursor()
    start = cursor.get(platform, 0)
    end = min(start + BATCH_SIZE, len(slugs))

    print(f"[{platform}] slugs {start}-{end} of {len(slugs)}")
    return slugs[start:end], end, len(slugs)


def _advance_cursor(platform, end, total):
    """Only called once a batch has finished successfully."""
    cursor = _read_cursor()
    cursor[platform] = 0 if end >= total else end
    _write_cursor(cursor)


def _fetch_greenhouse(slug):
    r = requests.get(GREENHOUSE_JOBS.format(slug), headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return [
        {
            "title": job.get("title", ""),
            "company": slug,
            "raw_description": _strip_html(job.get("content", "")),
        }
        for job in r.json().get("jobs", [])
    ]


def _fetch_lever(slug):
    r = requests.get(LEVER_JOBS.format(slug), headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return [
        {
            "title": job.get("text", ""),
            "company": slug,
            "raw_description": job.get("descriptionPlain", ""),
        }
        for job in r.json()
    ]


def _append(jobs):
    """Append one JSON object per line, so batches accumulate."""
    with RAW_FILE.open("a", encoding="utf-8") as f:
        for job in jobs:
            f.write(json.dumps(job) + "\n")


def _run_platform(url, fetcher, platform):
    slugs, end, total = _next_batch(url, platform)
    jobs = []
    failed = 0
    errors = {}
    done = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(fetcher, s): s for s in slugs}
        for future in as_completed(futures):
            try:
                jobs.extend(future.result())
            except Exception as e:
                failed += 1
                name = type(e).__name__
                errors[name] = errors.get(name, 0) + 1

            done += 1
            if done % 100 == 0 or done == len(slugs):
                print(f"[{platform}] {done}/{len(slugs)} | {len(jobs)} jobs | {failed} failed")

    if errors:
        print(f"[{platform}] errors: {errors}")
    print(f"[{platform}] done — {len(jobs)} jobs from {len(slugs) - failed} boards\n")

    _append(jobs)
    _advance_cursor(platform, end, total)
    return jobs


def download(limit=None):
    count = 0

    count += len(_run_platform(GREENHOUSE_COMPANIES_URL, _fetch_greenhouse, "greenhouse"))

    print("pausing 30s before lever ...\n")
    time.sleep(30)

    count += len(_run_platform(LEVER_COMPANIES_URL, _fetch_lever, "lever"))

    total = sum(1 for _ in RAW_FILE.open(encoding="utf-8"))
    print(f"[{SOURCE_NAME}] +{count} this batch, {total} total in {RAW_FILE}")
    return RAW_FILE


def load(limit=None):
    download()

    rows = [json.loads(line) for line in RAW_FILE.open(encoding="utf-8")]
    df = pd.DataFrame(rows)
    df["source"] = SOURCE_NAME
    return df


if __name__ == "__main__":
    result = load()
    print(result.shape)