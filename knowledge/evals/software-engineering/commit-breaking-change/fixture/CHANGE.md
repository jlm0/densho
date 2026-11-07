# Change

The function `parse_config(path)` in `config.py` no longer accepts the path as a string. It now takes a `pathlib.Path` object only. Code that passes a string now raises `TypeError`.

The change also adds the function `load_defaults()`, which returns the default settings.
