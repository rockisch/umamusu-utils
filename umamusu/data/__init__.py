from ..shared import get_logger, state

logger = get_logger(__name__)


KINDS = ["characard", "supportcard", "factor", "skill"]


def data_main(args):
    if not state.storage_path.exists():
        logger.error(f"storage folder does not exist: {state.storage_path}")
        return

    if args.command == "extract":
        from .extract import data_extract

        data_extract(args)


__all__ = ["data_main", KINDS]
