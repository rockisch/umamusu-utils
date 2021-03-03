# Uma Musume Utils

Utils for scrapping UmaMusume files.

## Requirements

You must insert into the `/storage` folder your own copy of the `meta` file.
It can be fetched from the game's root dir: `/root/data/data/jp.co.cygames.umamusume/files`.

Each script outputs to a different folder/file in `/storage`, so check that folder after running a script to get the resulting data.

Some scripts have dependencies, run `pip install -r requirements.txt` to install all of them.

## Utils

All utils reside inside the `scripts` folder.

### data_download

Downloads **ALL** game assets according to your `meta` file.
If the game is updated, all you have to do is update the `meta` file and re-run this script.
This only downloads new files, you can set `SKIP_EXISTING` to false inside the script to force a full re-download.

**IMPORTANT** If doing a full download, this will suck your machine's network as hard as a JAV actress.
Set `ASYNC_DOWNLOAD` to false to download in a less aggressive way.

### items_extract

Extracts stuff related to items.

### story_extract

Extract the strings related to the in-game stories.
This only extracts new files, you can set `SKIP_EXISTING` to `False` inside the script to force a full extraction.
