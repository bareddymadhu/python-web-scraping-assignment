# Realizan Technologies – Multi-Source Web Scraping Assignment

## Overview

This project implements the assignment as a small ETL pipeline:

`Scrape both sites -> Clean -> Validate -> Deduplicate -> Consolidate -> Save`

Sources:
- https://books.toscrape.com/
- https://quotes.toscrape.com/

The scraper follows each site's `li.next > a` link until no next page exists. Page numbers are never hard-coded.

## Python and dependencies

Python 3.10–3.12 is recommended. Install from `requirements.txt` in a virtual environment.

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run the full pipeline with one command:

```powershell
python main.py
```

Run tests:

```powershell
pytest -q
```

## Page observations

### Books to Scrape
- Record: `article.product_pod`
- Title: `h3 > a` and the `title` attribute
- Price: `p.price_color`
- Rating: class on `p.star-rating`
- Link: `h3 > a[href]`
- Next page: `li.next > a`

### Quotes to Scrape
- Record: `div.quote`
- Quote text: `span.text`
- Author: `small.author`
- Tags: `a.tag`
- Source URL: the page on which the quote appears
- Next page: `li.next > a`

## Common data model

The CSV columns are:

`source, source_url, name_or_title, category, price, rating, author, tags, description, scraped_at`

Fields not supplied by a source are left empty. No fake values are invented.

For this implementation, book category and description are left empty because obtaining them would require additional detail-page requests. This keeps the required listing-page scrape focused and avoids unnecessary traffic.

## HTTP and error handling

`base_scraper.py` provides one shared `requests.Session` with:
- a User-Agent
- a timeout
- retries for 429, 500, 502, 503 and 504
- exponential retry backoff
- a 0.5 second pause between successful requests

A failed page is logged as an error and stops that source; the other source is still attempted. Missing individual elements are handled without crashing the complete run.

## Cleaning

`processing/cleaning.py` provides separate functions for:
- whitespace and non-breaking-space cleanup
- removing curly quote marks
- converting prices such as `£51.77` to `51.77`
- converting ratings such as `Three` to `3`
- lowercasing, sorting and joining quote tags with `;`
- validating HTTP/HTTPS URLs

## Validation

A record must have a known source, a non-empty `name_or_title`, and a valid-looking HTTP/HTTPS URL. If present, price must be numeric and non-negative, and rating must be an integer from 1 to 5.

Validation failures are retained in `output/validation_rejections.json` and counted by reason in the summary report.

## Duplicate detection

Fingerprints use SHA-256 over normalized identifying fields.

- Books: `source + normalized title`
- Quotes: `source + normalized author + first 50 normalized characters of quote`

Normalization lowercases text, removes punctuation and collapses whitespace. Therefore differences such as leading/trailing spaces or capitalization are treated as duplicates.

Duplicates are removed from the final CSV. Unit tests intentionally create duplicates to prove the logic even though the practice sites normally contain unique records.

## Outputs

After a successful run:

- `output/final_dataset.csv` — unique valid consolidated records
- `output/summary_report.json` — collection, cleaning, rejection, duplicate and timing metrics
- `logs/scraper.log` — timestamped progress, warnings and errors
- `output/validation_rejections.json` — rejected records and reasons

The expected reconciliation is:

`final = raw - rejected - duplicates`

## Assumptions and limitations

- The two supplied practice sites remain publicly accessible and retain compatible HTML structure.
- The program does not bypass security controls or authentication.
- Book category and description are not scraped from detail pages in this version; those cells remain empty as permitted by the assignment.
- Quote `source_url` is the listing page where the quote was observed, rather than the author profile URL.
- The scraper is intentionally sequential and rate-limited rather than parallel.

## AI usage

See `AI_USAGE.md` for the required disclosure.
