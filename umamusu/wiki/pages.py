import re

from wiki.templates import Templates

RE_PAGE = r'^(?P<before>^.*){{%s\n(?P<data>.*)\n}}(?P<after>.*)$'


def parse_page_source(source: str, kind: Templates):
    match = re.match(RE_PAGE % kind.value, source, re.DOTALL)
    if not match:
        raise Exception()

    source_data = match['data']
    lines = source_data.split('\n')
    data = {}
    for line in lines:
        key, value = line.split('=', 1)
        data[key[1:]] = value

    return data, match['before'], match['after']


def encode_page_source(data: dict, kind: Templates, before: str='', after: str=''):
    if not before and kind.before:
        before = kind.before

    source_data = '\n'.join([f'|{k}={str(v)}' for k, v in data.items()])
    texts = [v for v in (before, '{{%s' % kind.value, source_data, '}}', after) if v]
    return '\n'.join(texts)
