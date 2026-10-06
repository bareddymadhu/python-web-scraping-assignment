from processing.validation import validate_record

def test_valid_record():
    record = {"source": "Books to Scrape", "source_url": "https://example.com/book", "name_or_title": "Book", "price": 10.0, "rating": 4}
    assert validate_record(record) == []

def test_invalid_record():
    record = {"source": "Unknown", "source_url": "bad", "name_or_title": "", "price": -1, "rating": 7}
    problems = validate_record(record)
    assert set(problems) == {"unknown_source", "missing_name", "invalid_url", "invalid_price", "invalid_rating"}
