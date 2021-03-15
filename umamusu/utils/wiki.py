def translate_references(text: str, references: dict):
    if 'NAME' in references:
        references['ASSET_NAME'] = '_'.join(references['NAME'].split(' '))

    for key, value in references.items():
        text = text.replace(f'${key}', value)

    return text
