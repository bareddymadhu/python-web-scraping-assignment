# AI_USAGE.md

## AI tool used

ChatGPT.

## How AI was used

AI was used to help:
- understand the assignment and break it into ETL stages
- design the project structure
- draft the shared HTTP/retry helper
- draft BeautifulSoup selectors and dynamic pagination
- design cleaning and validation functions
- design the SHA-256 duplicate fingerprint
- draft unit tests and documentation
- review edge cases around missing HTML elements and request failures

## Representative prompts

1. "Build a Python Requests + BeautifulSoup ETL pipeline for Books to Scrape and Quotes to Scrape with dynamic next-link pagination."
2. "Design duplicate detection that ignores whitespace, capitalization and punctuation, using the identifying fields specified by the assignment."
3. "Create unit tests for text, price, rating, validation and duplicate detection without making network requests."

## Review and changes

AI output was treated as a draft, not as automatically correct code. The final implementation was structured to match the assignment's required filenames, fields, 0.5-second request pause, dynamic pagination, logging, validation reasons, duplicate fingerprinting and CSV/JSON outputs.

Important implementation choices were reviewed against the assignment reference, including:
- using `lxml` with BeautifulSoup
- setting UTF-8 response encoding
- preserving missing fields as empty values rather than inventing data
- keeping source-specific scraping code separate from processing code
- using the required Books-vs-Quotes duplicate identity rules
- keeping one source failure from stopping the other source

## Verification

The unit tests are designed to run without internet access. Before submission, run `pytest -q`, then run `python main.py` from a clean virtual environment and inspect the generated CSV, JSON summary and log.
