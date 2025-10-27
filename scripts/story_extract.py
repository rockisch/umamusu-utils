import enum
import io
import os
import tempfile
import sys
import json
import itertools
import sqlite3
import UnityPy
from dataclasses import dataclass
from pathlib import Path
from typing import List
from UnityPy.enums import ClassIDType
from collections import defaultdict

from utils import get_meta_conn, get_master_conn, get_storage_folder, get_logger, get_girls_dict, _derive_asset_key

logger = get_logger(__name__)

SKIP_EXISTING = True
HPATHS = False

if HPATHS:
    DATA_ROOT = get_storage_folder('dat')
else:
    DATA_ROOT = get_storage_folder('data')

DECRYPTED_DATA_ROOT = get_storage_folder("data_decrypted")
STORY_ROOT = get_storage_folder('story')
MAIN_STORY_TABLE = 'main_story_data'
EVENT_STORY_TABLE = 'story_event_story_data'
CHARACTER_STORY_TABLE = 'chara_story_data'
MAIN_STORY_SEG_MAX = 5
MAIN_STORY_SEG_COLUMNS = ', '.join([
    column
    for i in range(1, MAIN_STORY_SEG_MAX + 1) for column in [f'"story_type_{i}"', f'"story_id_{i}"']
])

class SegmentKind(enum.Enum):
    TEXT = 1
    LIVE = 2
    SPECIAL = 3
    RACE = 4

    def __str__(self):
        if self is self.TEXT:
            return 'text'
        if self is self.LIVE:
            return 'live'
        if self is self.SPECIAL:
            return 'special'
        if self is self.RACE:
            return 'race'

@dataclass
class LineData:
    name: str
    text: str

@dataclass
class SegmentData:
    id: int
    order: int
    kind: SegmentKind

    def get_lines(self) -> List[LineData]:
        return fetch_segment_lines(self)

@dataclass
class EpisodeData:
    id: int
    segments: List[SegmentData]

@dataclass
class StoryData:
    id: int
    kind: str
    episodes: List[EpisodeData]

def story_extract():
    save_stories(fetch_main_story_data())
    save_stories(fetch_event_story_data())
    save_stories(fetch_character_story_data())

def save_stories(story_data: list[StoryData]):
    meta_conn = get_meta_conn()
    try:
        for story in story_data:
            path = Path(STORY_ROOT, story.kind, f'{story.id}.txt')
            with open(path, 'w', encoding='utf8') as f:
                for episode in story.episodes:
                    f.write(f'Episode {episode.id}:\n')
                    for segment in episode.segments:
                        f.write(f'Segment {segment.id} ({segment.kind.name.lower()}):\n')
                        for line in fetch_segment_lines(segment, meta_conn):
                            f.write(f'  {line.name}: {line.text.replace("\n", " ")}\n')
                        f.write('\n')
    finally:
        meta_conn.close()

def format_story(story: StoryData):
    episodes_data = []
    for episode in story.episodes:
        segments_data = []
        for segment in episode.segments:
            lines_data = []
            try:
                lines = segment.get_lines()
            except Exception as e:
                logger.error(e, extra={'story': story})
                lines = []

            for line in lines:
                if line.text:
                    line_data = '{}{}\n'.format(('- {}:\n'.format(line.name) if line.name else ''), line.text.replace('\r\n', '\n'))
                    lines_data.append(line_data)

            segment_data = '\n'.join(lines_data)
            segments_data.append(f'Segment {segment.order} ({str(segment.kind)}):\n{segment_data}')

        episode_data = '\n'.join(segments_data)
        episodes_data.append(f'Episode {episode.id}:\n{episode_data}')

    story_data = '\n'.join(episodes_data)
    return story_data

def fetch_segment_lines(segment: SegmentData, meta_conn):
    lines = []
    if segment.kind is not SegmentKind.TEXT:
        return lines
    story_id_str = str(segment.id).zfill(9)
    storyline_basename = f'storytimeline_{story_id_str}'
    db_asset_name = f"story/data/{story_id_str[:2]}/{story_id_str[2:6]}/{storyline_basename}"

    asset_key_row = next(meta_conn.execute('SELECT "e", "h" FROM "a" WHERE "n" = ?', (db_asset_name,)), None)
    if not asset_key_row:
        logger.warning(f"Asset '{db_asset_name}' not found in meta database. Skipping...")
        return lines
    
    asset_hash = asset_key_row['h']
    is_encrypted = asset_key_row['e'] != 0
    
    if HPATHS:
        source_path = Path(DATA_ROOT, asset_hash[:2].upper(), asset_hash)
    else:
        source_path = Path(DATA_ROOT, db_asset_name)
    decrypted_path = Path(DECRYPTED_DATA_ROOT, db_asset_name)
    temp_file_path = None
    env = None
    try:
        if is_encrypted and decrypted_path.exists():
            logger.info(f"Loading pre-decrypted asset: {decrypted_path}...")
            env = UnityPy.load(str(decrypted_path))
        else:
            if not source_path.exists():
                logger.info(f"Source file not found, skipping: {source_path}...")
                return lines

            with open(source_path, 'rb') as f:
                data = bytearray(f.read())

            if is_encrypted:
                decryption_key = _derive_asset_key(asset_key_row['e'])
                if decryption_key and len(data) > 256:
                    key_len = len(decryption_key)
                    for i in range(256, len(data)):
                        data[i] ^= decryption_key[i % key_len]

            ram_disk_dir = "/dev/shm" if sys.platform == "linux" else None
            with tempfile.NamedTemporaryFile(delete=False, dir=ram_disk_dir) as temp_f:
                temp_f.write(data)
                temp_file_path = temp_f.name
            env = UnityPy.load(temp_file_path)

    except Exception as e:
        logger.error(f"Failed to load or process asset from {db_asset_name}: {e}")
        return lines
    finally:
        if temp_file_path:
            os.unlink(temp_file_path)

    if not env.assets:
        return lines

    timeline_tree = None
    clip_objects = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        tree = obj.read_typetree()
        if tree.get("m_Name") == storyline_basename:
            timeline_tree = tree
        else:
            clip_objects[obj.path_id] = tree

    if not timeline_tree:
        found_names = [
            obj.read_typetree().get("m_Name", "Unnamed")
            for obj in env.objects if obj.type.name == "MonoBehaviour"
        ]
        logger.warning(f"Could not find timeline object named '{storyline_basename}'. Found these instead: {found_names}. Skipping...")
        return lines

    for block in timeline_tree['BlockList']:
        for clip in block['TextTrack']['ClipList']:
            clip_path_id = clip.get('m_PathID')
            if not clip_path_id or clip_path_id not in clip_objects:
                continue
            type_tree = clip_objects[clip_path_id]
            lines.append(LineData(type_tree['Name'], type_tree['Text']))
    return lines

def fetch_main_story_data():
    master_conn = get_master_conn()
    try:
        part_episodes = defaultdict(list)
        for row in master_conn.execute(f'SELECT "part_id", "episode_index", {MAIN_STORY_SEG_COLUMNS} FROM "{MAIN_STORY_TABLE}"'):
            part_id = row['part_id']
            episode_index = row['episode_index']

            segment_types = [row[f'story_type_{i}'] for i in range(1, MAIN_STORY_SEG_MAX + 1)]
            segment_ids = [row[f'story_id_{i}'] for i in range(1, MAIN_STORY_SEG_MAX + 1)]

            segments = []
            for i, (story_type, story_id) in enumerate(zip(segment_types, segment_ids), start=1):
                if story_type == 0:
                    continue
                try:
                    kind = SegmentKind(story_type)
                    segments.append(SegmentData(story_id, i, kind))
                    logger.info(f"Fetching main story... Part ID: {part_id} Episode: {episode_index}")
                except ValueError:
                    logger.warning(f"Unknown SegmentKind '{story_type}' found in part_id {part_id}, episode {episode_index}. Skipping...")
                    continue

            part_episodes[part_id].append(EpisodeData(episode_index, segments))

        main_story_data = [StoryData(part_id, 'main', episodes) for part_id, episodes in part_episodes.items()]
        return main_story_data
    finally:
        master_conn.close()

def fetch_event_story_data():
    master_conn = get_master_conn()
    try:
        story_event_episodes = defaultdict(list)
        for row in master_conn.execute(f'SELECT "story_event_id", "episode_index_id", "story_id_1" FROM "{EVENT_STORY_TABLE}"'):
            event_id = row['story_event_id']
            episode_index = row['episode_index_id']
            story_id = row['story_id_1']
            segments = [SegmentData(story_id, 1, SegmentKind.TEXT)]
            story_event_episodes[event_id].append(EpisodeData(episode_index, segments))
            logger.info(f"Fetching event story... Event ID: {event_id} Episode: {episode_index}")

        event_story_data = [StoryData(event_id, 'event', episodes) for event_id, episodes in story_event_episodes.items()]
        return event_story_data
    finally:
        master_conn.close()

def fetch_character_story_data():
    master_conn = get_master_conn()
    try:
        chara_episodes = defaultdict(list)
        for row in master_conn.execute(f'SELECT "chara_id", "episode_index", "story_id" FROM "{CHARACTER_STORY_TABLE}"'):
            chara_id = row['chara_id']
            episode_index = row['episode_index']
            story_id = row['story_id']
            segments = [SegmentData(story_id, 1, SegmentKind.TEXT)]
            chara_episodes[chara_id].append(EpisodeData(episode_index, segments))
            logger.info(f"Fetching character story... Character ID: {chara_id} Episode: {episode_index}")

        character_story_data = [StoryData(chara_id, 'chara', episodes) for chara_id, episodes in chara_episodes.items()]
        return character_story_data
    finally:
        master_conn.close()

if __name__ == '__main__':
    story_extract()
