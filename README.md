# Random Quote

A simple CLI to pick a random quote from a collection.

## Features

- Pick a random quote from your collection
- Add and remove quotes
- Search quotes using regular expressions
- Prevent repeats until all quotes have been shown
- Store quotes locally for personal use

## Getting Started

First clone the repository:
```
git clone https://github.com/fspivack/random-quote.git
```
Note that you might want to create and activate a Python virtual environment in which to install `random-quote`. Now `cd` into the cloned directory, and type:
```
pip install .
```
Now you can run the program by simply typing:
```
random-quote
```

## Quote Storage

On first run, the program copies a starter set of quotes into a collection.

You can then freely add and remove quotes without affecting the original set.

The included quotes are intended only as examples. Users are encouraged to curate their own collection.

## Options

- **`-l` `--list-quotes`** List all quotes including their id
- **`--re-list`** List all quotes with a particular regex pattern. By default this searches the quotes. Use `--field` to specify searching `author` or `both`
- **`-a`** **`--add`** Add a quote. If you do not also add an author, via the option `--author`, the author field will be left blank
- **`--author`** Use in conjunction with `--add` to specify an author for the provided quote
- **`-r`** **`--remove`** Remove a quote by id
- **`--re-remove`** Remove a quote matching the regex specified. Use `--field` to specify removing according to `author` or `both`. Otherwise it will remove according to quote
- **`--field`** Specify one of the options `quote`, `author` or `both`. This will apply the pattern supplied to option `--re-list` or `--re-remove` to the field specified. By default, it is set to `quote`
- **`--no-repeats`** Set the program to not repeat quotes when giving random quotes, until all quotes have been cycled through
- **`--allow-repeats`** Set the program to allow repeats when giving random quotes. This is the default

## Examples

To just print a random quote:

```
random-quote
```
Output:
```
"Talk is cheap. Show me the code." -- Linus Torvalds
```

To add the quote "This is a test", by anon, you can type:
```
random-quote --add "This is a test" --author "anon"
```

To remove all quotes by authors starting "A", type:
```
random-quote --re-remove "A" --field "author"
```

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you'd like to get in touch, please feel free to contact me at spivack.f@gmail.com.

I'm always happy to hear about potential collaborations or projects.