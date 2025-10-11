# Umamusu-Utils

Utils for scrapping honse game files.

## Requirements

You must insert into the `/storage` folder your own copy of the `meta` file and the `master` folder.
You can grab them from the game's root dir: `/data/data/jp.co.cygames.umamusume/files`.

All scripts have required dependencies, run `pip install -r requirements.txt` to install all of them.

## Utils

All utils reside inside the `scripts` folder.

### `data_download.py`

Downloads **ALL** game assets according to your `meta` file.
If the game is updated, all you have to do is update the `meta` file and re-run this script.
This only downloads new files, you can set `SKIP_EXISTING` to false inside the script to force a full re-download.

**IMPORTANT** If doing a full download, this will suck your machine's network dry.
Set `ASYNC_DOWNLOAD` to false to download in a less aggressive way.
The output files are located at `storage/data`.

### `items_extract.py`

Extracts stuff related to items. Output file can be found at `storage/items.txt`.

### `story_extract.py`

Extracts the strings related to the in-game stories.
This only extracts new files, you can set `SKIP_EXISTING` to `False` inside the script to force a full extraction.
The output files are located at `storage/story`.

### `decrypt_meta.py`

Creates a one-to-one copy of the `meta` file with no encryption. Output file can be found at `storage/meta_decrypted`.
