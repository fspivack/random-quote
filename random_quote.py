#!/usr/bin/env python3
"""
Print and manage quotes. If executed without any arguments, the program will
print a random quote.
"""

# Copyright (c) 2026 Francesca Spivack
# Licensed under the MIT License: https://opensource.org/licenses/MIT

import argparse
import random
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional

QUOTES_PATH = Path(__file__).parent / "quotes.txt"
STARTER_QUOTES_PATH = Path(__file__).parent / "starter-quotes.txt"
STATEFILE_PATH = Path(__file__).parent / "allow-repeats.txt"
USED_QUOTES_PATH = Path(__file__).parent / "used-quotes.txt"


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


def get_random_quote(quotes: List[List[str]]) -> str:
    with open(STATEFILE_PATH, "r") as s:
        state = s.read()

    if state == "False":
        if not USED_QUOTES_PATH.exists():
            # todo: Check this is the best way
            open(USED_QUOTES_PATH, "a").close()
        with open(USED_QUOTES_PATH, "r+") as s:
            used_quotes = s.readlines()
            used_quotes = [x.split(";;") for x in used_quotes]
            available_quotes = [x for x in quotes if x not in used_quotes]
            if not available_quotes:
                # Empty the file
                s.truncate(0)
                available_quotes = quotes
    else:
        available_quotes = quotes
    current_quote = random.choice(available_quotes)
    if state == "False":
        with open(USED_QUOTES_PATH, "a") as s:
            s.write(f"{current_quote[0]};;{current_quote[1]}")

    return format_quote(current_quote)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not STATEFILE_PATH.exists():
        with open(STATEFILE_PATH, "w") as s:
            s.write("True")

    if not QUOTES_PATH.exists():
        shutil.copyfile(STARTER_QUOTES_PATH, QUOTES_PATH)

    with open(QUOTES_PATH, "r") as q:
        quotes = q.readlines()

    quotes = [x.split(";;") for x in quotes]

    if args.author and not args.add:
        parser.error("'--author' requires '--add'")
    # Removing this because args.field is always set
    # if args.field and not (args.re_list or args.re_remove):
    #     parser.error("'--field' requires '--re-list' or '--re-remove'")

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
        with open(QUOTES_PATH, "a") as q:
            # Note that if an author is not specified, 'args.author'
            # is blank
            q.write(f"{args.add};;{args.author if args.author else ''}\n")
    if args.remove:
        for i, quote in enumerate(quotes):
            if i == int(args.remove):
                quotes.remove(quote)
        with open(QUOTES_PATH, "w") as q:
            for line in quotes:
                q.write(f"{line[0]};;{line[1]}")
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
            for line in to_be_kept:
                q.write(f"{line[0]};;{line[1]}")

    if args.no_repeats:
        with open(STATEFILE_PATH, "w") as s:
            s.write("False")
            open(USED_QUOTES_PATH, "a").close()
    elif args.allow_repeats:
        with open(STATEFILE_PATH, "w") as s:
            s.write("True")

    if len(sys.argv) <= 1:
        print(get_random_quote(quotes))


if __name__ == "__main__":
    main()
