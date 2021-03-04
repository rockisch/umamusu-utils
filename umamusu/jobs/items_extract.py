import sqlite3
import logging
import enum
from dataclasses import dataclass
from pathlib import Path
from typing import List
from jobs.story_extract import DATA_ROOT

from utils import STORAGE_ROOT, get_master_conn
from utils.dumpers import JsonDumper


logger = logging.getLogger(__name__)


CATEGORY_ITEM_NAME = 23
CATEGORY_ITEM_DESC = 24


CONSUMABLES_ITEMS = {
    20,  # TP Juice
    21,  # Ninjin Juice
    34,  # Stopwatch
    150, # PvP items
}
ENCHANCEMENT_ITEMS = {
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
    if category_id in ENCHANCEMENT_ITEMS:
        return 'Enchancement Item'
    if category_id in TICKET_ITEMS:
        return 'Ticket'
    if category_id in OTHER_ITEMS:
        return 'Other'
    if category_id in NON_ITEMS:
        return ''



@dataclass
class ItemRow:
    id: str
    icon: str
    jpname: str
    description: str
    category: int
    category_string: str
    uses: int
    obtain: str


def items_extract(dumper=JsonDumper):
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
    items = []
    for item_id, category_id, limit_num, texts in master_conn.execute(query):
        item_id = str(item_id).zfill(5)
        texts = texts.split('|', 1)

        category_name = get_category_name(category_id)
        if category_name is None:
            logger.warning('unkown item category id', category_id)
            category_name = ''

        assets = dumper.get_unity_assets(f'item/item_icon_{item_id}')
        icon_path = assets[0].save(f'Item_Icon_{item_id}.png')
        dumper.dump(f'item/item_{item_id}', ItemRow(item_id, icon_path, texts[0], texts[1], category_id, category_name, limit_num, ''))

if __name__ == '__main__':
    items_extract()
