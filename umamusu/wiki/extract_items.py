import logging

from utils import get_master_conn, unity
from wiki.templates import Templates
from wiki.pages import dump_page_file


logger = logging.getLogger(__name__)


CATEGORY_ITEM_NAME = 23
CATEGORY_ITEM_DESC = 24


CONSUMABLES_ITEMS = {
    20,  # TP Juice
    21,  # Ninjin Juice
    34,  # Stopwatch
    150, # PvP items
}
ENHANCEMENT_ITEMS = {
    11,  # Most enchancements
    30,  # Support Lvl up coin
    93,  # Rainbow Horseshoe
    160, # Horseshoes
}
TICKET_ITEMS = {
    40,  # Most tickets
    41,  # 3* ticket
    42,  # SSR ticket
    140  # TODO(rockisch): Daily Tickets are stored here?
}
OTHER_ITEMS = {
    97,  # Statue
    99,  # Clover
    103, # Friend Points
    161, # Prestige
}
NON_ITEMS = {
    90,  # Carrot Gems
    91,  # Golden Horseshoe Coin
    94,  # Cassino Horseshoe Coin
    98,  # TODO(rockisch): Extra Friend is stored in any tab?
    100, # Event Pts
    110, # Big Pencil Tazuna
}


def get_category_name(category_id):
    if category_id in CONSUMABLES_ITEMS:
        return 'Consumable Item'
    if category_id in ENHANCEMENT_ITEMS:
        return 'Enhancement Item'
    if category_id in TICKET_ITEMS:
        return 'Ticket'
    if category_id in OTHER_ITEMS:
        return 'Other'
    if category_id in NON_ITEMS:
        return ''


def extract_items():
    master_conn = get_master_conn()
    query = """
        SELECT "id", "item_category", "limit_num", group_concat("text", '|')
          FROM (
             SELECT "item_data"."id",
                    "item_data"."item_category",
                    "item_data"."limit_num",
                    "text_data"."text"
               FROM "item_data"
              INNER JOIN "text_data"
                 ON "text_data"."index" = "item_data"."id"
                AND "text_data"."category" IN (23, 24)
              ORDER BY "text_data"."category"
          )
       GROUP BY "id"
       ORDER BY "id"
    """
    for item_id, category_id, limit_num, texts_agg in master_conn.execute(query):
        item_id = str(item_id).zfill(5)
        jpname, description = texts_agg.split('|', 1)

        category_name = get_category_name(category_id)
        if category_name is None:
            logger.warning('unknown item category id', category_id)
            category_name = ''

        icon = unity.get_unity_assets(f'item/item_icon_{item_id}')[0]
        icon.name = f'{icon.name[0].upper()}{icon.name[1:]}.png'
        item = {
            'id': int(item_id),
            'name': '$NAME',
            'jpname': jpname,
            'jpdescription': description,
            'icon': icon,
            'category': category_id,
            'category_string': category_name,
        }
        dump_page_file(item, jpname, Templates.ITEM, item_id, assets=[icon])


if __name__ == '__main__':
    extract_items()
