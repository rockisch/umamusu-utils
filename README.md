# Uma Musume Utils

Utils for scrapping UmaMusume files.

## Requirements

You must insert into the root folder your own copy of the `meta` file.
It can be fetched from the game's root dir: `/root/data/data/jp.co.cygames.umamusume/files`.

Some python scripts have dependencies, run `pip install -r requirements.txt` to install all of them.

## Utils

All utils reside inside the `scripts` folder.

### data_download

Downloads **ALL** game assets according to your `meta` file.
If the game is updated, all you have to do is update the `meta` file and re-run this script.
The script only downloads new files, you can set `SKIP_EXISTING` to false inside the script to force a full re-download.

**IMPORTANT** If doing a full download, this will suck your machine's network as hard as a JAV actress.
Set `ASYNC_DOWNLOAD` to false to download in a less aggressive way.

Data downloaded by this script will be stored at `/data`.

### story_extract

Extract the strings related to the in-game stories.
We then store these strings in a json file, which may be used later for translations.

Data extracted by this script will be stored at `/story`.
