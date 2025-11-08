# Uma Musume Utils

Utils for scrapping Uma Musume assets and descriptive data.

## Usage

These tools implement 2 basic functionalities: asset dumping (images, videos, BGMs, etc), and data dumping (character sheets, skill conditions, inheritance factors, etc):

```sh
# Extract supportcard and skill icon images to 'storage/assets/'
uv run main.py assets dump --kind supportcard skill
uv run main.py assets extract --kind supportcard skill

# Extracts skill data (name, description, etc) to 'storage/data/skill.json'
uv run main.py data extract --kind skill
```

The first argument specified whether you want to deal with game files (`assets`) or game data (`data`).

You can find more information about each command and subcommand by appending `-h` at the end of a command (e.g.: `uv run main.py assets -h`).

## Requirements

The recommended way to run the project is by using [`uv`](https://github.com/astral-sh/uv).

Some game DB files are also needed depending on what you're trying to extract:
- `assets`: Requires `meta` DB file
- `data`: Requires `master.mdb` DB file

By default the script will search for them under `%APPDATA%\LocalLow\Cygames\Umamusume`, but you can also specify their location with CLI options.

## TODO

- **Asset Downloading**: Allow downloading assets instead of requiring a game installation. This makes it a lot easier to run these scripts in environments without a game installation.
- **Extract more assets/data kinds**: The project structure makes it pretty easy to extract other kinds of data (stories, background images, etc), it just takes a bit of time to check what is stored where.
- **Extract story data**: Story data (as in, the story text, chapter names, etc) is a bit more annoying to extract. If you need it right now, it is still implemented in the [`old`](https://github.com/rockisch/umamusu-utils/tree/old) branch.

## Previous Version

A previous version of this project is available under the [`old`]((https://github.com/rockisch/umamusu-utils/tree/old)) branch, in case someone depended on it.
