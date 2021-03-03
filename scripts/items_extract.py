import sqlite3
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from utils import STORAGE_ROOT, get_master_conn


logger = logging.getLogger(__name__)


CATEGORY_ITEM_NAME = 23
CATEGORY_ITEM_DESC = 24


@dataclass
class ItemRow:
    id: int
    category_id: int
    name: str
    description: str


def items_extract():
    master_conn = get_master_conn()
    query = """
        SELECT "id", "item_category", group_concat("text", '|')
          FROM (
             SELECT "item_data"."id", "item_data"."item_category", "text_data"."text"
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
    for item_id, category_id, texts in master_conn.execute(query):
        item_id = int(item_id)
        category_id = int(category_id)
        texts = texts.split('|', 1)

        items.append(ItemRow(item_id, category_id, texts[0], texts[1]))

    data = format_items(items)
    with open(Path(STORAGE_ROOT, 'items.txt'), 'w', encoding='utf8') as f:
        f.write(data)


def format_items(items: List[ItemRow]):
    return '\n\n'.join(format_item(item) for item in items)


def format_item(item: ItemRow):
    return f"id={item.id}\ncategory={item.category_id}\njpname={item.name}\ndescription={item.description}"


if __name__ == '__main__':
    items_extract()
