from random_quote import random_quote

# Realised there's not much point to this, because that's not how the program
# will be used. Retrieving/adding/removing from the collection is instantaneous
# even with a very large collection of quotes

NUMBER_OF_QUOTES = 1000


def generate_quotes() -> list[list[list[str]]]:
    quotes = [[f"Quote {i}", f"Author {i}"] for i in range(NUMBER_OF_QUOTES)]
    return quotes


def test_performance(tmp_path) -> list[list[str]]:
    f = tmp_path / "tmpfile.txt"
    quotes = generate_quotes()
    for quote in quotes:
        random_quote.main(["--add", quote[0], "--author", quote[1]], f)
