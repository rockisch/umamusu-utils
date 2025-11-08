# Uma Musume Utils

Utils for scrapping Uma Musume assets and descriptive data.

## Usage

```sh
# Extracts skill data (name, description, etc) to 'storage/data/skill.json'
uv run main.py data extract --kind skill

# Extract supportcard and skill icon images to 'storage/assets/'
uv run main.py assets dump --kind supportcard skill
uv run main.py assets extract --kind supportcard skill
```

## Requirements

The recommended way to run the project is using [`uv`](https://github.com/astral-sh/uv).

Some DB files are also needed depending on what you're trying to extract:
- `data`: Requires `master.mdb` DB file
- `extract`: Requires `meta` DB file

By default the script will search for them under `%APPDATA%\LocalLow\Cygames\Umamusume`, but you can also specify their location with CLI options.

## Previous Version

A previous version of this project is available under the `old` branch, in case someone depended on it.
