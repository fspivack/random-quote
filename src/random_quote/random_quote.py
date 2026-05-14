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

# todo: Restructure the directory
# todo: Use proper logging
# todo: Test with large number of quotes

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from platformdirs import user_data_dir, user_state_dir

STARTER_QUOTES_PATH = Path(__file__).parent / "starter-quotes.txt"
QUOTES_DIR = Path(user_data_dir("random-quote"))
STATE_DIR = Path(user_state_dir("random-quote"))
QUOTES_PATH = QUOTES_DIR / "quotes.json"
STATEFILE_PATH = STATE_DIR / "allow-repeats.txt"
USED_QUOTES_PATH = STATE_DIR / "used-quotes.txt"


def format_quote(quote: List[str], i: Optional[int] = None) -> str:
    """Format a quote for printing"""
    # This should always work, unless you've edited the quotes file directly
    # Also, if there is no known author (even anon), the author is left blank
    if i is None:
        return f'"{quote[0]}" -- {quote[1]}'
    return f'id {i}: "{quote[0]}" -- {quote[1]}'


def matches_any(pattern: str, items: List[str]) -> bool:
    """Check if 'pattern' matches any of the items in 'items'"""
    for item in items:
        if re.match(pattern, item):
            return True
    return False


def get_quote_hash(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_in_quotes(quotes: List[List[str]]) -> str:
    # Rename the following:
    quotes_formatted = [
        {
            "id": i,
            "hash": get_quote_hash(x[0]),
            "quote": x[0].strip(),
            "author": x[1].strip(),
        }
        for i, x in enumerate(quotes)
    ]
    return quotes_formatted


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


def get_random_quote(quotes_json: List[Dict[str, str]]) -> str:
    with open(STATEFILE_PATH, "r") as s:
        state = s.read()

    if state == "False":
        if not USED_QUOTES_PATH.exists():
            # todo: Check this is the best way
            open(USED_QUOTES_PATH, "a").close()
        with open(USED_QUOTES_PATH, "r+") as s:
            # Using 'splitlines' so that we don't have the newline chars
            used_quote_hashes = s.read().splitlines()
            available_quotes = [
                x for x in quotes_json if x["hash"] not in used_quote_hashes
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
            s.write(f"{current_quote['hash']}\n")

    return format_quote([current_quote["quote"], current_quote["author"]])


def main() -> None:
    QUOTES_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    parser = build_parser()
    args = parser.parse_args()
    # Validate
    if args.author and not args.add:
        parser.error("'--author' requires '--add'")
    if args.remove:
        try:
            int(args.remove)
        except ValueError:
            parser.error(
                "Argument passed to '-r' or '--remove' must be an integer"
            )

    if not STATEFILE_PATH.exists():
        with open(STATEFILE_PATH, "w") as s:
            s.write("True")

    if not QUOTES_PATH.exists():
        with open(STARTER_QUOTES_PATH, "r") as q:
            starter_quotes = q.readlines()
        starter_quotes = [x.split(";;") for x in starter_quotes]
        with open(QUOTES_PATH, "w") as f:
            json.dump(load_in_quotes(starter_quotes), f, indent=4)

    with open(QUOTES_PATH, "r") as q:
        quotes_json = json.load(q)

    quotes = [[x["quote"], x["author"]] for x in quotes_json]

    if args.list_quotes:
        for i, quote in enumerate(quotes):
            print(format_quote(quote, i))
    elif args.re_list:
        for i, quote in enumerate(quotes):
            if args.field == "quote":
                if matches_any(args.re_list, [quote[0]]):
                    print(format_quote(quote, i))
            elif args.field == "author":
                if matches_any(args.re_list, [quote[1]]):
                    print(format_quote(quote, i))
            else:
                if matches_any(args.re_list, quote):
                    print(format_quote(quote, i))

    if args.add:
        with open(QUOTES_PATH, "w") as q:
            # Note that if an author is not specified, 'args.author'
            # is blank
            quotes.append([args.add, args.author if args.author else ""])
            json.dump(load_in_quotes(quotes), q, indent=4)

    if args.remove:
        i = int(args.remove)
        new_quotes_json = [x for x in quotes_json if x["id"] != i]
        # Here we recalculate the ids
        new_quotes = [[x["quote"], x["author"]] for x in new_quotes_json]
        with open(QUOTES_PATH, "w") as q:
            json.dump(load_in_quotes(new_quotes), q, indent=4)
    if args.re_remove:
        to_be_kept = []
        for quote in quotes:
            # The point of the following line is so that, if consecutive
            # quotes are to be removed, we don't screw that up by changing
            # the iterator
            if args.field == "quote":
                if not matches_any(args.re_remove, [quote[0]]):
                    to_be_kept.append(quote)
            elif args.field == "author":
                if not matches_any(args.re_remove, [quote[1]]):
                    to_be_kept.append(quote)
            else:
                if not matches_any(args.re_remove, quote):
                    to_be_kept.append(quote)
        with open(QUOTES_PATH, "w") as q:
            json.dump(load_in_quotes(to_be_kept), q, indent=4)

    if args.no_repeats:
        with open(STATEFILE_PATH, "w") as s:
            s.write("False")
            open(USED_QUOTES_PATH, "a").close()
    elif args.allow_repeats:
        with open(STATEFILE_PATH, "w") as s:
            s.write("True")

    if len(sys.argv) <= 1:
        print(get_random_quote(quotes_json))


if __name__ == "__main__":
    main()
