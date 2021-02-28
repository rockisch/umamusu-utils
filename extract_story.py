import enum
import json
import sqlite3
import UnityPy
from dataclasses import dataclass
from pathlib import Path
from UnityPy.enums import ClassIDType

LIMIT = 200
MAIN_STORY_SEG_COUNT = 5

ROOT = Path(__file__).with_name('story')
ROOT.mkdir(parents=True, exist_ok=True)
DATA_ROOT = Path(__file__).with_name('data')
if not DATA_ROOT.exists():
    raise Exception("you must first download the game data using 'download.py'")
QUERY_STORY_SEGMENTS_COLUMNS = ', '.join([
    column
    for i in range(1, MAIN_STORY_SEG_COUNT + 1) for column in [f'"story_type_{i}"', f'"story_id_{i}"']
])

class StoryType(enum.Enum):
    TEXT = 1
    LIVE = 2
    SPECIAL = 3
    RACE = 4

    def __str__(self):
        if self is StoryType.TEXT:
            return 'text'
        if self is StoryType.LIVE:
            return 'live'
        if self is StoryType.SPECIAL:
            return 'special'
        if self is StoryType.RACE:
            return 'race'

@dataclass
class StorySegment:
    story_type: StoryType
    story_id: int

    def __str__(self):
        return f'<Segment {self.story_id}, type={self.story_type}>'

@dataclass
class MainStoryData:
    part_id: int
    episode_index: int
    story_number: int
    stories_segments: list[StorySegment]

    def __str__(self):
        return f'<Story {self.part_id}/{self.episode_index}>'


def get_main_story_data(main_story: MainStoryData):
    story_data = []
    for segment_id, segment in enumerate(main_story.stories_segments, start=1):
        segment_data = []
        if segment.story_type is StoryType.TEXT:
            story_id = str(segment.story_id).zfill(9)
            segment_data_path = Path(DATA_ROOT, 'story/data', story_id[:2], story_id[2:6], f'storytimeline_{story_id}')
            env = UnityPy.load(segment_data_path.as_posix())
            if not env.assets:
                print(f'ERROR: unable to find {segment} file for story {main_story}')
                print('SKIPPING')
                continue

            objects = {}
            timeline = None
            for obj in env.objects:
                if obj.type != ClassIDType.MonoBehaviour:
                    continue

                if not timeline:
                    obj_data = obj.read()
                    if obj_data.name == f'storytimeline_{story_id}':
                        timeline = obj_data

                objects[obj.path_id] = obj

            if not timeline:
                print(f'ERROR: unable to find timeline for segment {segment} n. {segment_id}')
                print('SKIPPING')
                continue

            for block in timeline.type_tree['BlockList']:
                for clip in block['TextTrack']['ClipList']:
                    obj = objects[clip['m_PathID']]
                    type_tree = obj.read().type_tree
                    segment_data.append({'name': type_tree['Name'], 'text': type_tree['Text']})

        story_data.append({'segment': segment_id, 'type': segment.story_type, 'data': segment_data})

    return story_data


def main(main_stories: list[MainStoryData]):
    for story in main_stories:
        story_data = get_main_story_data(story)
        story_path = Path(ROOT, 'main', str(story.part_id), f'{story.episode_index}.json')
        story_path.parent.mkdir(parents=True, exist_ok=True)
        with story_path.open('w', encoding='utf8') as f:
            json.dump(story_data, f, ensure_ascii=False, indent=4, default=str)


master_conn = sqlite3.connect('master.mdb')
offset = 0
while True:
    main_stories = []
    for row in master_conn.execute(f'SELECT "part_id", "episode_index", "story_number", {QUERY_STORY_SEGMENTS_COLUMNS} FROM "main_story_data" LIMIT {LIMIT} OFFSET {offset}'):
        main_data, segment_data = row[:3], row[3:]
        story_segments = []
        skip = False
        for story_type, story_id in zip(segment_data[::2], segment_data[1::2]):
            if story_type != 0:
                story_segments.append(StorySegment(StoryType(story_type), story_id))

        if skip:
            continue

        main_stories.append(MainStoryData(*main_data, story_segments))

    if not main_stories:
        break

    main(main_stories)
    offset += len(main_stories)
    if offset % 1000:
        print('MAIN STORY PROGRESS:', offset)

