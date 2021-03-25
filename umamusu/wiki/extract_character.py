import logging
from datetime import datetime

from utils import get_master_conn, unity
from wiki.templates import Templates
from wiki.pages import dump_page_file


logger = logging.getLogger(__name__)


QUERY_ATTRS = ['speed', 'stamina', 'pow', 'guts', 'wiz']
WIKI_ATTRS = ['speed', 'stamina', 'power', 'guts', 'wisdom']
QUERY_DISTANCE = ['short', 'mile', 'middle', 'long']
WIKI_DISTANCE = ['short', 'mile', 'medium', 'long']
QUERY_STRATEGY = ['nige', 'senko', 'sashi', 'oikomi']
WIKI_STRATEGY = ['runner', 'leader', 'betweener', 'chaser']
GROUND = ['turf', 'dirt']

CHAR_QUERY_COLUMNS = [
    c.format(a) for a in QUERY_ATTRS
    for c in ['"card_data"."talent_{}"']
]
CHAR_WIKI_COLUMNS = [
    c.format(a) for a in WIKI_ATTRS
    for c in ['{}_growth_bonus']
]
RARITY_QUERY_APTITUDE_COLUMNS = [
    '"card_rarity_data"."proper_distance_{}"'.format(a) for a in QUERY_DISTANCE
] + [
    '"card_rarity_data"."proper_running_style_{}"'.format(a) for a in QUERY_STRATEGY
] + [
    '"card_rarity_data"."proper_ground_{}"'.format(a) for a in GROUND
]
RARITY_WIKI_APTITUDE_COLUMNS = [
    'aptitude_{}'.format(a) for a in WIKI_DISTANCE + WIKI_STRATEGY + GROUND
]


def extract_character():
    master_conn = get_master_conn()
    char_query_columns_str = ','.join(CHAR_QUERY_COLUMNS)
    query = f"""
        SELECT "chara_data"."id",
               "name_text_data"."text",
               "va_text_data"."text"
          FROM "chara_data"
          JOIN "text_data" AS "name_text_data"
            ON "name_text_data"."index" = "chara_data"."id" AND "name_text_data"."category" = 6
          JOIN "text_data" AS "va_text_data"
            ON "va_text_data"."index" = "chara_data"."id" AND "va_text_data"."category" = 7
    """
    for chara_id, jpname, jpva in master_conn.execute(query):
        chara = {
            'id': chara_id,
            'name_jp': jpname,
            'va_jp': jpva,
        }
        dump_page_file(chara, jpname, Templates.CHARACTER_BIO, chara_id)

        card_query = f"""
            SELECT "card_data"."id", "default_rarity",
                "title_text_data"."text" AS "title",
                {char_query_columns_str}
            FROM "card_data"
            JOIN "text_data" AS "title_text_data"
              ON "title_text_data"."index" = "card_data"."id" AND "title_text_data"."category" = 5
           WHERE "chara_id" = {chara_id}
        """
        for card_id, default_rarity, jptitle, *char_columns in master_conn.execute(card_query):
            card_id = str(card_id).zfill(5)
            jptitle = jptitle[1:-1]
            wiki_columns_data = {k: v for k, v in zip(CHAR_WIKI_COLUMNS, char_columns)}

            lowest_unique_skill = None
            # highest_unique_skill = None
            rarity_attrs_culumns_str = ','.join(QUERY_ATTRS)
            rarity_query_columns_str = ','.join(RARITY_QUERY_APTITUDE_COLUMNS)
            rarity_query = f"""
                SELECT "rarity", "skill_set"."skill_id1", {rarity_attrs_culumns_str}, {rarity_query_columns_str}
                FROM "card_rarity_data"
                JOIN "skill_set"
                    ON "skill_set"."id" = "card_rarity_data"."skill_set"
                WHERE "card_rarity_data"."card_id" = {card_id}
            """
            rarity_data = {}
            for rarity, unique_skill_id, *rarity_columns in master_conn.execute(rarity_query):
                attrs_columns, aptitude_columns = rarity_columns[:len(WIKI_ATTRS)], rarity_columns[len(WIKI_ATTRS):]
                rarity_data.update({f'{k}{rarity}': v for k, v in zip(WIKI_ATTRS, attrs_columns)})
                rarity_data.update({k: v for k, v in zip(RARITY_WIKI_APTITUDE_COLUMNS, aptitude_columns)})

                if not lowest_unique_skill or rarity < lowest_unique_skill[0]:
                    lowest_unique_skill = (rarity, unique_skill_id)
                # TODO(rockisch): find how to get upgraded unique
                # if not highest_unique_skill or rarity > highest_unique_skill[0]:
                #     print('SETTING HIGHEST UNIQUE', rarity, unique_skill_id)
                #     highest_unique_skill = (rarity, unique_skill_id)

            icon = unity.get_unity_assets(f'chara/chr{chara_id}/chr_icon_{chara_id}_{card_id}_01')[0]
            icon.name = f'{icon.name[0].upper()}{icon.name[1:]}.png'
            resized_size = (icon.image.width, int(icon.image.height * 1.1))
            icon.image = icon.image.resize(resized_size)


            chara_card = {
                'id': card_id,
                'chara_id': chara_id,
                'title_jp': jptitle,
                'base_star': default_rarity,
                'icon': icon,
                'unique_skill': lowest_unique_skill[1],
                **rarity_data,
                **wiki_columns_data,
            }
            dump_page_file(chara_card, jptitle, Templates.CHARACTER_DATA, card_id, assets=[icon])


if __name__ == '__main__':
    extract_character()
