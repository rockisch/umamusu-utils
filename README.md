# Uma Musume Utils

This repo contains stuff that will help you handle with data from Uma Musu.

## Requirements

You must insert into the root folder your own copies of the `meta` and `master.mdb` files.

## Utils

### download

Downloads **ALL** game files according to your `meta` file.
If the game is updated, all you have to do is update the `meta` file and re-run this script.
You can set `SKIP_EXISTING` to true inside the script to only download new files.

Data downloaded by this script will be stored at `/data`.

### extract_story

Extract the strings related to the in-game stories.
We then store these strings in a json file, which may be used later for translations.

Data extracted by this script will be stored at `/story`.
