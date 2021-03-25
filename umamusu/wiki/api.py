from pathlib import Path
from typing import List

import requests

from utils import get_logger, chunk_iter
from wiki.templates import Templates


logger = get_logger(__name__)


from utils import get_secret_file

ENDPOINT = ''
USERNAME = ''
PASSWORD = ''
try:
    secret = get_secret_file()['wiki']
    ENDPOINT = secret['endpoint']
    USERNAME = secret['username']
    PASSWORD = secret['password']
except:
    raise Exception('secret file not found, unable to upload files')

API_ENDPOINT = ENDPOINT + '/api.php'
REST_ENDPOINT = ENDPOINT + '/rest.php/v1'


class APISession:
    def __init__(self, *args, **kwargs):
        self.session = requests.Session()
        self.auth = False

    def __get_csrf_token(self):
        if not self.auth:
            self.__session_auth()

        resp = self.session.get(API_ENDPOINT, params={
            'action': 'query',
            'meta': 'tokens',
            'format': 'json',
        })
        data = resp.json()

        csrf_token = data['query']['tokens']['csrftoken']
        return csrf_token

    def __session_auth(self):
        # Get Token
        resp = self.session.get(API_ENDPOINT, params={
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json',
        })
        data = resp.json()
        login_token = data['query']['tokens']['logintoken']

        # Session Auth
        resp = self.session.post(API_ENDPOINT, data={
            'action': 'login',
            'lgname': USERNAME,
            'lgpassword': PASSWORD,
            'lgtoken': login_token,
            'format': 'json',
        })
        data = resp.json()
        if data['login']['result'] == 'Failed':
            raise Exception(data)

        self.auth = True

    def get_page(self, kind: Templates, id: str):
        params = {
            'format': 'json',
            'action': 'cargoquery',
            'limit': 1,
            'tables': kind.cargo_table,
            'fields': 'id,_pageName=name',
            'where': f'item.id = {id}'
        }
        resp = self.session.get(API_ENDPOINT, params=params)
        data = resp.json()
        if 'cargoquery' not in data:
            return

        page_title = data['cargoquery'][0]['title']['name']
        resp = self.session.get(REST_ENDPOINT + f'/page/{page_title}')
        data = resp.json()
        if not 'id' in data:
            return

        return data

    def bulk_get_pages(self, kind: Templates, ids: List):
        ids_str = ','.join([str(i) for i in ids[1:]])
        print(ids_str)
        params = {
            'format': 'json',
            'action': 'cargoquery',
            'tables': kind.cargo_table,
            'fields': 'id,_pageName=name',
            'where': f'item.id IN ({ids_str})'
        }
        resp = self.session.get(API_ENDPOINT, params=params)
        data = resp.json()
        if 'cargoquery' not in data:
            return {}

        pages = {}
        print(data)
        for page in data['cargoquery']:
            page_data = page['title']
            pages[page_data['id']] = page_data['name']


    def update_page(self, target_page: dict, source: str):
        # 'target_page' should be result of 'get_page'
        csrf_token = self.__get_csrf_token()
        update_data = {
            'token': csrf_token,
            'source': source,
            'comment': 'Automatic update done by Tazuna-bot.',
            'latest': target_page['latest']
        }
        page_title = target_page['title']
        resp = self.session.put(REST_ENDPOINT + f'/page/{page_title}', json=update_data)
        data = resp.json()

    def create_redirect(self, to_title: str, from_title: str):
        self.create_page(from_title, f'#REDIRECT [[{to_title}]]')

    def create_page(self, title: str, source: str):
        csrf_token = self.__get_csrf_token()
        create_data = {
            'token': csrf_token,
            'title': title,
            'source': source,
            'comment': 'Automatic creation done by Tazuna-bot',
        }
        resp = self.session.post(REST_ENDPOINT + f'/page', json=create_data)
        data = resp.json()

    def upload_asset(self, file: Path, filename: str=None):
        csrf_token = self.__get_csrf_token()
        params = {
            'token': csrf_token,
            'action': 'upload',
            'filename': filename or file.name,
            'format': 'json',
        }
        filesize = file.stat().st_size
        # Direct upload for small files, chunked upload for the big boys
        if filesize < 1_024_000:
            file_data = {'file': (filename, file.open('rb'), 'multipart/form-data')}
            resp = self.session.post(API_ENDPOINT, data=params, files=file_data)
            data = resp.json()
        else:
            with file.open('rb') as f:
                chunks = chunk_iter(f)
                chunk = next(chunks)
                chunk_data = {'chunk': ('0' + file.suffix, chunk, 'multipart/form-data')}
                resp = self.session.post(API_ENDPOINT, data={
                    **params,
                    'stash': 1,
                    'filesize': filesize,
                    'offset': 0,
                }, files=chunk_data)
                data = resp.json()

                for i, chunk in enumerate(chunks):
                    chunk_data = {'chunk': (str(i) + file.suffix, chunk, 'multipart/form-data')}
                    resp = self.session.post(API_ENDPOINT, data={
                        **params,
                        'stash': 1,
                        'filesize': filesize,
                        'filekey': data['upload']['filekey'],
                        'offset': data['upload']['offset'],
                    }, files=chunk_data)
                    data = resp.json()

                resp = self.session.post(API_ENDPOINT, data={
                    **params,
                    'filekey': data['upload']['filekey'],
                })
                data = resp.json()

        if 'upload' in data:
            upload = data['upload']
            if upload['result'] == 'Warning':
                warnings = upload['warnings']
                # Duplicate means there's already a file uploaded with a different name
                if 'duplicate' in warnings:
                    remote_filename = warnings['duplicate'][0]
                    self.create_redirect(f'File:{remote_filename}', f'File:{filename}')
            logger.info('file upload success: %s', filename)
        else:
            logger.error('file upload failed: %s', filename)
