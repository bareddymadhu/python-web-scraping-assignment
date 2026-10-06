from processing.cleaning import clean_price, clean_rating, clean_tags, clean_text, strip_quotes

def test_clean_text():
    assert clean_text("  Hello \n World \xa0") == "Hello World"

def test_strip_quotes():
    assert strip_quotes('“Hello world”') == "Hello world"

def test_price():
    assert clean_price("£51.77") == 51.77

def test_rating():
    assert clean_rating("star-rating Three") == 3

def test_tags():
    assert clean_tags(["Python", " data", "python"]) == "data;python;python"
