import asyncio

from jobs import data_download, items_extract
from wiki.upload import upload_files
from utils.dumpers import WikiDumper


# Ensure data is always updated
data_download()

# Extract data to 'wiki' folder
items_extract(WikiDumper)

# Upload the data
loop = asyncio.get_event_loop()
loop.run_until_complete(upload_files())
