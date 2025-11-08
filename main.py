import argparse
from pathlib import Path

from umamusu import assets, data
from umamusu.shared import state

parser = argparse.ArgumentParser(prog="Umamusu Utils")
subparsers = parser.add_subparsers(required=True)

parser_assets = subparsers.add_parser("assets")
parser_assets.add_argument(
    "command", choices=("download", "dump", "extract"), default="extract"
)
parser_assets.add_argument("--skip-i", type=int)
parser_assets.add_argument("--skip-existing", action="store_true")
parser_assets.add_argument("--async-download", action="store_true")
parser_assets.add_argument("--kind", nargs="*")
parser_assets.set_defaults(handler=assets.assets_main)

parser_data = subparsers.add_parser("data")
parser_data.add_argument("command", choices=("extract",), default="extract")
parser_data.add_argument("--kind", nargs="*")
parser_data.set_defaults(handler=data.data_main)

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

args = parser.parse_args()

state.version = args.version
state.master_path = args.master_file
state.meta_path = args.meta_file
state.appdata_path = args.appdata_folder
state.storage_path = args.storage_folder
state.log_path = args.log

args.handler(args)
