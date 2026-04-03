# Random Quote

A simple CLI to pick a random quote from a collection.

## Features

- Pick a random quote from your collection
- Add and remove quotes
- Search quotes using regular expressions
- Prevent repeats until all quotes have been shown
- Store quotes locally for personal use

## Getting Started

Clone the repository and run:

```bash
$ ./random_quote.py
```

This will produce a random quote from the starter collection.

## Quote Storage

On first run, the program copies a starter set of quotes into a local, git-ignored file.

You can then freely add, remove, and modify quotes without affecting the original set.

The included quotes are intended only as examples. Users are encouraged to curate their own collection.

## Options

- **`-l` `--list-quotes`** List all quotes including their id
- **`--re-list`** List all quote with a particular regex pattern. By default this searches the quotes. Use `--field` to specify searching `author` or `both`
- **`-a`** **`--add`** Add a quote. If you do not also add an author, via the option `--author`, the author field will be left blank
- **`--author`** Use in conjunction with `--add` to specify an author for the provided quote
- **`-r`** **`--remove`** Remove a quote by id
- **`--re-remove`** Remove a quote matching the regex specified. Use `--field` to specify removing according to `author` or `both`. Otherwise it will remove according to quote
- **`--field`** Specify one of the options `quote`, `author` or `both`. This will apply the pattern supplied to option `--re-list` or `--re-remove` to the field specified. By default, it is set to `quote`
- **`--no-repeats`** Set the program to not repeat quotes when giving random quotes. When all quotes have been cycled through, this is reset
- **`--allow-repeats`** Set the program to allow repeats when giving random quotes. This is the default

## Examples

To just print a random quote:

```bash
$ ./random_quote.py
```
Output:
```
"Talk is cheap. Show me the code." -- Linus Torvalds
```

To add the quote "This is a test", by anon, you can type:
```bash
$ ./random_quote.py --add "This is a test" --author "anon"
```

To remove all quotes by authors starting "A", type:
```bash
$ ./random_quote.py --re-remove "A" --field "author"
```

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you'd like to get in touch, please feel free to contact me at spivack.f@gmail.com.

I'm always happy to hear about potential collaborations or projects.