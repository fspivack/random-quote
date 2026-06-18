#!/usr/bin/env python3
"""
Print and manage quotes. If executed without any arguments, the program will
print a random quote.
"""

# Copyright (c) 2026 Francesca Spivack
# Licensed under the MIT License: https://opensource.org/licenses/MIT

# Note that the conversion to using json objects has resulted in an inefficient
# way of running. This may be corrected at a later date

# Conscious decision not to split 'main' into too many functions, because that
# would require passing loads of arguments
# Update: May split off a few functions for unit testing

# todo: Use proper logging? Probably no need
# todo: Test with large number of quotes
# todo: Clean up of auto-generated files if the user wants to get rid of them?
# todo: Decide whether to put min Py version as 3.10

import argparse
import hashlib
import json
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict
from importlib.resources import files

from platformdirs import user_data_dir, user_state_dir

QUOTES_DIR = Path(user_data_dir("random-quote"))
STATE_DIR = Path(user_state_dir("random-quote"))
QUOTES_PATH = QUOTES_DIR / "quotes.json"
STATEFILE_PATH = STATE_DIR / "allow-repeats.txt"
USED_QUOTES_PATH = STATE_DIR / "used-quotes.txt"


# @dataclass
# class AppConfig:
#     # Putting this here so that args to main don't get too unwieldy
#     quotes_file: str | None = None
#     used_quotes_file: str | None = None

# Custom types for ease of reference
Quote = list[str]
class StoredQuote(TypedDict):
    qid: int
    qhash: str
    quote: str
    author: str

def get_starter_quotes_path():
    return files("random_quote").joinpath("starter-quotes.txt")
    
def format_quote(quote: Quote, i: int | None = None) -> str:
    """Format a quote for printing"""
    # This should always work, unless you've edited the quotes file directly
    # Also, if there is no known author (even anon), the author is left blank
    if i is None:
        return f'"{quote[0]}" -- {quote[1]}'
    return f'id {i}: "{quote[0]}" -- {quote[1]}'


def matches_any(pattern: str, items: list[str]) -> bool:
    """Check if 'pattern' matches any of the items in 'items'"""
    for item in items:
        if re.match(pattern, item):
            return True
    return False


def get_quote_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_in_quotes(quotes: list[Quote]) -> list[StoredQuote]:
    """Format quotes for storing in file"""
    # Rename the following:
    return [
        {
            "qid": i,
            "qhash": get_quote_hash(x[0]),
            "quote": x[0].strip(),
            "author": x[1].strip(),
        }
        for i, x in enumerate(quotes)
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Print and manage quotes")

    parser.add_argument(
        "-l", "--list-quotes", action="store_true", help="List all quotes"
    )
    parser.add_argument(
        "--re-list", help="List all quotes with specified regex pattern"
    )
    parser.add_argument("-a", "--add", help="Add a quote")
    parser.add_argument(
        "--author",
        help="Specify the author of a quote added with the '--add' option",
    )
    parser.add_argument("-r", "--remove", help="Remove a quote")
    parser.add_argument("--re-remove", help="Remove a quote using regex")
    parser.add_argument(
        "--field",
        choices=["quote", "author", "both"],
        help=(
            "What field to apply '--re-list' or '--re-remove' to. "
            "Options are 'quote', 'author' or 'both'"
        ),
        default="quote",
    )
    parser.add_argument(
        "--no-repeats",
        action="store_true",
        help=(
            "Set the program to not repeat quotes when giving random quotes "
            "unless all quotes have been displayed already"
        ),
    )
    parser.add_argument(
        "--allow-repeats",
        action="store_true",
        help="Set the program to allow repeats when giving random quotes",
    )

    return parser


def get_random_quote(quotes_json: list[StoredQuote]) -> str:
    """Select a random quote from the user's collection"""
    with open(STATEFILE_PATH) as s:
        state = s.read()

    if state == "False":
        if not USED_QUOTES_PATH.exists():
            # todo: Check this is the best way
            open(USED_QUOTES_PATH, "a").close()
        with open(USED_QUOTES_PATH, "r+") as s:
            # Using 'splitlines' so that we don't have the newline chars
            used_quote_hashes = s.read().splitlines()
            available_quotes = [
                x for x in quotes_json if x["qhash"] not in used_quote_hashes
            ]
            if not available_quotes:
                # Empty the file
                s.truncate(0)
                available_quotes = quotes_json
    else:
        available_quotes = quotes_json
    current_quote = random.choice(available_quotes)
    if state == "False":
        with open(USED_QUOTES_PATH, "a") as s:
            s.write(f"{current_quote['qhash']}\n")

    return format_quote([current_quote["quote"], current_quote["author"]])

def initialise_statefile() -> None:
    if not STATEFILE_PATH.exists():
        with open(STATEFILE_PATH, "w") as s:
            s.write("True")

def initialise_quote_list(quotes_path: Path) -> None:
    if not quotes_path.exists():
        with get_starter_quotes_path().open() as q:
            starter_quotes_raw = q.readlines()
        starter_quotes = [x.split(";;") for x in starter_quotes_raw]
        with open(quotes_path, "w") as f:
            json.dump(load_in_quotes(starter_quotes), f, indent=4)

def ensure_directories_exist() -> None:
    QUOTES_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if args.author and not args.add:
        parser.error("'--author' requires '--add'")
    if args.remove:
        try:
            int(args.remove)
        except ValueError:
            parser.error(
                "Argument passed to '-r' or '--remove' must be an integer"
            )

def get_all_quotes(quotes_path: Path) -> tuple[list[Quote], list[StoredQuote]]:
    with open(quotes_path) as q:
        quotes_json = json.load(q)
    quotes = [[x["quote"], x["author"]] for x in quotes_json]
    return quotes, quotes_json

def list_quotes(quotes: list[Quote]) -> None:
    for i, quote in enumerate(quotes):
        print(format_quote(quote, i))

def re_list_quotes(quotes: list[Quote], pattern: str, field: str) -> None:
    for i, quote in enumerate(quotes):
        if field == "quote":
            if matches_any(pattern, [quote[0]]):
                print(format_quote(quote, i))
        elif field == "author":
            if matches_any(pattern, [quote[1]]):
                print(format_quote(quote, i))
        else:
            if matches_any(pattern, quote):
                print(format_quote(quote, i))

def add_quote(quotes_path: Path, quotes: list[Quote], quote: str, author: str | None = None) -> None:
    with open(quotes_path, "w") as q:
        # Note that if an author is not specified, 'author' is blank
        quotes.append([quote, author if author else ""])
        json.dump(load_in_quotes(quotes), q, indent=4)

def remove_quote(quotes_path: Path, to_remove: str, quotes_json: list[StoredQuote]) -> None:
    i = int(to_remove)
    new_quotes_json = [x for x in quotes_json if x["qid"] != i]
    # Here we recalculate the ids
    new_quotes = [[x["quote"], x["author"]] for x in new_quotes_json]
    with open(quotes_path, "w") as q:
        json.dump(load_in_quotes(new_quotes), q, indent=4)

def re_remove_quote(quotes_path: Path, quotes: list[Quote], pattern: str, field: str) -> None:
    # The point of the following line is so that, if consecutive quotes are to
    # be removed, we don't screw that up by changing the iterator
    to_be_kept = []
    for quote in quotes:
        if field == "quote":
            if not matches_any(pattern, [quote[0]]):
                to_be_kept.append(quote)
        elif field == "author":
            if not matches_any(pattern, [quote[1]]):
                to_be_kept.append(quote)
        else:
            if not matches_any(pattern, quote):
                to_be_kept.append(quote)
    with open(quotes_path, "w") as q:
        json.dump(load_in_quotes(to_be_kept), q, indent=4)    

def toggle_allow_repeats(args: argparse.Namespace) -> None:
    if args.no_repeats:
        with open(STATEFILE_PATH, "w") as s:
            s.write("False")
            open(USED_QUOTES_PATH, "a").close()
    elif args.allow_repeats:
        with open(STATEFILE_PATH, "w") as s:
            s.write("True")

def print_quote(quotes_json: list[StoredQuote]) -> None:
    # Very unsure about keeping this as a separate function!
    print(get_random_quote(quotes_json))

def main(
    args_overwrite: list[str] | None = None, file_overwrite: str | None = None
) -> None:
    ensure_directories_exist()

    quotes_path = Path(file_overwrite) if file_overwrite else QUOTES_PATH

    parser = build_parser()
    args = parser.parse_args(args_overwrite)
    validate_args(args, parser)

    initialise_statefile()
    initialise_quote_list(quotes_path)

    quotes, quotes_json = get_all_quotes(quotes_path)
    
    if args.list_quotes:
        list_quotes(quotes)
    elif args.re_list:
        re_list_quotes(quotes, args.re_list, args.field)

    if args.add:
        add_quote(quotes_path, quotes, args.add, args.author)

    if args.remove:
        remove_quote(quotes_path, args.remove, quotes_json)
        
    if args.re_remove:
        re_remove_quote(quotes_path, quotes, args.re_remove, args.field)

    toggle_allow_repeats(args)

    if len(sys.argv) <= 1:
        print_quote(quotes_json)

if __name__ == "__main__":
    main()
