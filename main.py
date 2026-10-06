import csv
import json
import logging
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
LOGS = ROOT / "logs"
OUTPUT.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.FileHandler(LOGS / "scraper.log", encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger("pipeline")

FIELDS = ["source", "source_url", "name_or_title", "category", "price", "rating", "author", "tags", "description", "scraped_at"]


def run_source(name, scraper):
    try:
        records = list(scraper.scrape())
        logger.info("Collected %d records from %s", len(records), name)
        return records
    except Exception:
        logger.exception("Source failed: %s", name)
        return []


def main():
    start = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()

    raw_by_source = {
        "Books to Scrape": run_source("Books to Scrape", BooksScraper()),
        "Quotes to Scrape": run_source("Quotes to Scrape", QuotesScraper()),
    }
    raw = [r for rows in raw_by_source.values() for r in rows]

    cleaned = [clean_record(r) for r in raw]
    cleaned_by_source = Counter(r["source"] for r in cleaned)

    valid = []
    rejected_by_source = defaultdict(int)
    rejected_reasons = Counter()
    rejected_records = []
    for record in cleaned:
        problems = validate_record(record)
        if problems:
            for reason in problems:
                rejected_reasons[reason] += 1
            rejected_by_source[record.get("source", "unknown")] += 1
            rejected_records.append({"record": record, "reasons": problems})
            logger.warning("Rejected %s: %s", record.get("name_or_title"), ", ".join(problems))
        else:
            valid.append(record)

    unique, duplicates = find_duplicates(valid)
    duplicate_by_source = Counter(r["source"] for r in duplicates)

    with open(OUTPUT / "final_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for record in unique:
            writer.writerow({field: record.get(field) for field in FIELDS})

    ended_at = datetime.now(timezone.utc).isoformat()
    duration = round(time.perf_counter() - start, 3)
    summary = {
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": duration,
        "collected_per_source": {k: len(v) for k, v in raw_by_source.items()},
        "cleaned_per_source": dict(cleaned_by_source),
        "rejected_total": len(rejected_records),
        "rejected_per_source": dict(rejected_by_source),
        "rejected_by_reason": dict(rejected_reasons),
        "duplicates_detected": len(duplicates),
        "duplicates_per_source": dict(duplicate_by_source),
        "final_record_count": len(unique),
    }
    with open(OUTPUT / "summary_report.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    with open(OUTPUT / "validation_rejections.json", "w", encoding="utf-8") as f:
        json.dump(rejected_records, f, indent=4, ensure_ascii=False)

    logger.info("Pipeline complete: %s", json.dumps(summary))


if __name__ == "__main__":
    main()
