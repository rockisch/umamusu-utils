HOSTNAME = "https://prd-storage-game-umamusume.akamaized.net/dl/resources/"


class DownloadContext:
    host: str
    is_async: bool


def assets_download(args):
    raise NotImplementedError("Download is not yet implemented in the new version")
