import json

from ..shared import Status, master_cursor, state
from . import logger


def characard_extract(args):
    with master_cursor() as cursor:
        cursor.execute("""
            SELECT c.id, c.chara_id, n.text
            FROM card_data c
            JOIN text_data n ON n."index" = c.id AND n.category = 4
            ORDER BY c.default_rarity DESC, c.id
        """)
        chara_card_rows = cursor.fetchall()

    chara_cards = []
    for card_id, chara_id, name in chara_card_rows:
        chara_cards.append(
            {
                "id": card_id,
                "chara_id": chara_id,
                "name": name,
            }
        )

    return [("characard.json", chara_cards)]


def supportcard_extract(args):
    with master_cursor() as cursor:
        cursor.execute("""
            SELECT c.id, c.rarity, c.command_id, c.start_date, n.text
            FROM support_card_data c
            JOIN text_data n ON n."index" = c.id AND n.category = 75
            ORDER BY c.rarity DESC, c.start_date, c.id
        """)
        support_card_rows = cursor.fetchall()

    support_cards = []
    for id, rarity, type, start_date, name in support_card_rows:
        support_cards.append(
            {
                "id": id,
                "name": name,
                "rarity": rarity,
                "type": type,
                "ts": start_date,
            }
        )

    return [("supportcard.json", support_cards)]


def factor_extract(args):
    with master_cursor() as cursor:
        cursor.execute("""
            SELECT f.factor_id, f.rarity, f.grade, f.factor_type, n.text, d.text
            FROM succession_factor f
            JOIN text_data n ON n."index" = f.factor_id AND n.category = 147
            JOIN text_data d ON d."index" = f.factor_id AND d.category = 172
        """)
        factor_rows = cursor.fetchall()

    factors = []
    for factor_id, rarity, grade, type, name, desc in factor_rows:
        factors.append(
            {
                "id": factor_id,
                "name": name,
                "description": desc,
                "rarity": rarity,
                "grade": grade,
                "type": type,
            }
        )

    return [("factor.json", factors)]


def skill_extract(args):
    with master_cursor() as cursor:
        cursor.execute("""
            SELECT s.id, s.rarity, s.skill_category, s.condition_1, s.condition_2, s.icon_id, n.text, d.text
            FROM skill_data s
            JOIN text_data n ON n."index" = s.id AND n.category = 47
            JOIN text_data d ON d."index" = s.id AND d.category = 48
        """)
        factor_rows = cursor.fetchall()

    skills = []
    for (
        skill_id,
        rarity,
        category,
        condition_1,
        condition_2,
        icon_id,
        name,
        desc,
    ) in factor_rows:
        skills.append(
            {
                "id": skill_id,
                "name": name,
                "description": desc,
                "rarity": rarity,
                "category": category,
                "condition_1": condition_1,
                "condition_2": condition_2,
                "icon_id": icon_id,
            }
        )

    return [("skill.json", skills)]


EXTRACTORS = {
    "supportcard": supportcard_extract,
    "characard": characard_extract,
    "factor": factor_extract,
    "skill": skill_extract,
}


def data_extract(args):
    kinds = args.kind
    if not kinds:
        kinds = list(EXTRACTORS.keys())

    data_path = state.storage_path / "data"
    data_path.mkdir(exist_ok=True)
    for kind in kinds:
        extractor = EXTRACTORS.get(kind)
        if not extractor:
            logger.error(f"invalid kind: {kind}")
            continue

        for data_filename, data in extractor(args):
            data_file = data_path / data_filename
            with data_file.open("w+") as file:
                json.dump(data, file, indent=2)

            logger.info(f"Extracted '{kind}' data to '{data_file}'!", status=Status.OK)
