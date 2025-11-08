import argparse
from pathlib import Path

from umamusu import assets, data
from umamusu.shared import state

parser = argparse.ArgumentParser(prog="Umamusu Utils")
subparsers = parser.add_subparsers(required=True)

# Generic
parser.add_argument("--version", choices=("en", "jp", "kr", "tw"), default="en")
parser.add_argument(
    "--master-file",
    help="Path to the master DB file",
    default=Path("./master.mdb"),
    type=Path,
)
parser.add_argument(
    "--meta-file",
    help="Path to the meta file",
    default=Path("./meta"),
    type=Path,
)
parser.add_argument(
    "--appdata-folder",
    help="Path to the AppData folder",
    default=Path.home() / "AppData/LocalLow/Cygames/Umamusume",
    type=Path,
)
parser.add_argument(
    "--storage-folder",
    help="Path where output data will be stored",
    default=Path("./storage"),
)
parser.add_argument("--log", help="Path to the log file (default: stdout)", type=Path)

# Assets
assets_parser = subparsers.add_parser(
    "assets",
    help="commands related to asset (images, videos, music, etc) extraction",
)
assets_parser.set_defaults(handler=assets.assets_main)
data_commands = assets_parser.add_subparsers(required=True, dest="command")

assets_download = data_commands.add_parser(
    "download",
    help="Downloads game blobs. Useful when you don't have a game installation on the machine (not yet implemented)",
)
assets_download.add_argument("--async-download", action="store_true")
assets_download.add_argument("--skip-existing", action="store_true")
assets_download.add_argument("--kind", nargs="*", choices=assets.KINDS)

assets_dump = data_commands.add_parser(
    "dump",
    help="Dumps images, videos, BGMs, etc stored in the game blobs",
)
assets_dump.add_argument("--skip-i", type=int)
assets_dump.add_argument("--skip-existing", action="store_true")
assets_dump.add_argument("--kind", nargs="*", choices=assets.KINDS)

assets_extract = data_commands.add_parser(
    "extract",
    help="Extracts files from the dump into user-manageable folders. Only takes into account data previously dumped with the 'assets dump' command",
)
assets_extract.add_argument("--kind", nargs="*", choices=assets.KINDS)

# Data
data_parser = subparsers.add_parser(
    "data",
    help="commands related to data (character sheets, skill conditions, inheritance factors, etc) extraction",
)
data_parser.set_defaults(handler=data.data_main)
data_commands = data_parser.add_subparsers(required=True, dest="command")

data_extract = data_commands.add_parser(
    "extract",
    help="Extracts data from the game's DB file",
)
data_extract.add_argument("--kind", nargs="*", choices=data.KINDS)

# Handling
args = parser.parse_args()

state.version = args.version
state.master_path = args.master_file
state.meta_path = args.meta_file
state.appdata_path = args.appdata_folder
state.storage_path = args.storage_folder
state.log_path = args.log

state.storage_path.mkdir(exist_ok=True)

args.handler(args)
