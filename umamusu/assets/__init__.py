from ..shared import get_logger, state

logger = get_logger(__name__)


KINDS = ["skill", "supportcard"]


def assets_main(args):
    if not state.storage_path.exists():
        logger.error(f"storage folder does not exist: {state.storage_path}")
        return

    if args.command == "download":
        from .download import assets_download

        assets_download(args)
    elif args.command == "dump":
        from .dump import assets_dump

        assets_dump(args)
    elif args.command == "extract":
        from .extract import assets_extract

        assets_extract(args)


__all__ = ["assets_main", "KINDS"]
