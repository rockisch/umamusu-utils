import argparse

from jobs import data_download, translate_meta
from wiki import upload, extract_data


parser = argparse.ArgumentParser(description='Uma Musume Scripts.')
parser.add_argument('action', choices=['download', 'translate', 'upload', 'extract'],
    help='specifies which action to run')

args = parser.parse_args()
if args.action == 'download':
    data_download()
elif args.action == 'upload':
    upload()
elif args.action == 'extract':
    extract_data()
