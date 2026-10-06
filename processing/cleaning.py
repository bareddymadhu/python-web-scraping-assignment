import re
from urllib.parse import urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def strip_quotes(value):
    text = clean_text(value)
    if not text:
        return None
    return text.strip('“”"')


def clean_price(value):
    if value is None:
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(value):
    if value is None:
        return None
    for word in re.findall(r"[A-Za-z]+", str(value).lower()):
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(value):
    if not value:
        return None
    tags = [clean_text(v).lower() for v in value if clean_text(v)] if isinstance(value, list) else [clean_text(v).lower() for v in str(value).split(";") if clean_text(v)]
    return ";".join(sorted(tags)) or None


def normalize_url(value):
    value = clean_text(value)
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return None


def clean_record(record):
    cleaned = dict(record)
    for field in ["source", "category", "author", "description", "availability"]:
        cleaned[field] = clean_text(cleaned.get(field))
    cleaned["name_or_title"] = strip_quotes(cleaned.get("name_or_title"))
    cleaned["price"] = clean_price(cleaned.get("price"))
    cleaned["rating"] = clean_rating(cleaned.get("rating"))
    cleaned["tags"] = clean_tags(cleaned.get("tags"))
    cleaned["source_url"] = normalize_url(cleaned.get("source_url"))
    return cleaned
