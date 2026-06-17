import tempfile

from random_quote import random_quote

NUMBER_OF_QUOTES = 10000


def generate_quotes() -> list[list[list[str]]]:
    quotes = [[f"Quote {i}", f"Author {i}"] for i in range(NUMBER_OF_QUOTES)]
    return quotes


def run_performance_test() -> list[list[str]]:
    f = tempfile.TemporaryFile()
    quotes = generate_quotes()
    for quote in quotes:
        random_quote.main(["--add", quote[0], "--author", quote[1]], f)
