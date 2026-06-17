from random_quote import random_quote


def test_format_quote() -> None:
    quote = ["This is a quote", "anon"]
    result = '"This is a quote" -- anon'
    assert random_quote.format_quote(quote) == result


def test_format_quote_with_id() -> None:
    quote = ["This is a quote", "anon"]
    result = 'id 5: "This is a quote" -- anon'
    assert random_quote.format_quote(quote, 5) == result


def test_matches_any() -> None:
    pattern = "T"
    items = ["Test", "Hello"]
    assert random_quote.matches_any(pattern, items)


def test_does_not_match_any() -> None:
    pattern = "A"
    items = ["Test", "Hello"]
    assert not random_quote.matches_any(pattern, items)
