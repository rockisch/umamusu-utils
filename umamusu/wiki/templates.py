import enum
from dataclasses import dataclass
from typing import List


@dataclass
class TemplateData:
    value: str
    cargo_table: str
    name_field: str
    before: str
    after: str
    fields: List[str]
    keep_original: List[str]


class Templates:
    ITEM = TemplateData('Item', 'items', 'name', None, None,
        ['id', 'icon', 'name_jp', 'description_jp', 'name', 'description', 'category', 'category_string', 'uses', 'obtain'],
        ['name', 'description'])
    CHARACTER_BIO = TemplateData('CharacterBio', 'characterbio', 'name', None, None,
        ['id', 'name_jp', 'name', 'va_jp', 'va'],
        ['name', 'va'])
    CHARACTER_DATA = TemplateData('CharacterData', 'characters', 'title', None, None,
        [
            'id', 'chara_id', 'art', 'title', 'title_jp', 'base_star', 'series', 'obtain', 'release_date', 'limited', 'link_gamewith', 'link_kamigame',
            *[f'{a}{i}' for a in ['speed', 'stamina', 'power', 'guts', 'wisdom'] for i in range(1, 6)],
            'speed_growth_bonus', 'stamina_growth_bonus', 'power_growth_bonus', 'guts_growth_bonus', 'wisdom_growth_bonus',
            'aptitude_turf', 'aptitude_dirt', 'aptitude_short', 'aptitude_mile', 'aptitude_medium', 'aptitude_long',
            'aptitude_runner', 'aptitude_leader', 'aptitude_betweener', 'aptitude_chaser',
            'awakening_materials',
            *[f'awakening{i}' for i in range(1, 5)],
            'events', 'objectives', 'model_file', 'model_texture',
        ],
        ['title'])
