import hashlib
import re


def _normalize(value):
    value = "" if value is None else str(value)
    value = re.sub(r"[^\w\s]", "", value.casefold())
    return " ".join(value.split())


def make_fingerprint(record):
    source = record.get("source", "")
    if source == "Books to Scrape":
        key = f"{source}|{_normalize(record.get('name_or_title'))}"
    else:
        quote = _normalize(record.get("name_or_title"))[:50]
        key = f"{source}|{_normalize(record.get('author'))}|{quote}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records):
    seen = set()
    unique, duplicates = [], []
    for record in records:
        fp = make_fingerprint(record)
        if fp in seen:
            duplicates.append(record)
        else:
            seen.add(fp)
            unique.append(record)
    return unique, duplicates
