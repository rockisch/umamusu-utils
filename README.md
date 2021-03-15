# Uma Musume Utils

Utils for scrapping UmaMusume files.

## Requirements

You must insert into the `storage` folder your own copy of the `meta` file. It's location depends on the OS:

* Android: `/root/data/data/jp.co.cygames.umamusume/files`
* Windows: `C:\Users\<USER>\AppData\LocalLow\Cygames\umamusume`

Each script outputs to a different folder/file in `/storage`, so check that folder after running a script to get the resulting data.

Some scripts have dependencies, run `pip install -r requirements.txt` to install all of them.

## Utils

All utils can be ran by running the `umamusu/run.py` script with the script name as the first argument.

### download

Downloads **ALL** game assets according to your `meta` file.
If the game is updated, all you have to do is update the `meta` file and re-run this script.
