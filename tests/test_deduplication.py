from processing.deduplication import find_duplicates

def test_books_duplicates_ignore_case_and_spaces():
    base = {"source": "Books to Scrape"}
    records = [
        {**base, "name_or_title": "Example Book Title"},
        {**base, "name_or_title": "  Example Book Title "},
        {**base, "name_or_title": "EXAMPLE BOOK TITLE"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 1
    assert len(dupes) == 2

def test_quote_duplicates():
    records = [
        {"source": "Quotes to Scrape", "author": "Alice", "name_or_title": "A quote here"},
        {"source": "Quotes to Scrape", "author": " alice ", "name_or_title": "A QUOTE HERE"},
    ]
    unique, dupes = find_duplicates(records)
    assert len(unique) == 1
    assert len(dupes) == 1
