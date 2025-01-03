import re
import config as cfg
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mindmap.mindmap_helper import MindmapTopic

config = cfg.get_config()

line_separator = config.LINE_SEPARATOR
indent_size = config.INDENT_SIZE
use_round = False
use_root = True

class MermaidTopic:
    def __init__(self, topic_text='', topic_level=0):
        self.topic_text = topic_text
        self.topic_level = topic_level

class MermaidMindmap:
    def __init__(self, mermaid_mindmap: str=''):
        self.mermaid_mindmap = mermaid_mindmap

        if self.mermaid_mindmap:
            if validate_mermaid(mermaid_mindmap):
                raise ValueError("The Mermaid mindmap is not valid.")
            self.mermaid_topics: list['MermaidTopic'] = self.parse_mermaid(mermaid_mindmap)
            self.max_topic_level: int = max(topic.topic_level for topic in self.mermaid_topics)
        else:
            self.mermaid_topics = []
            self.max_topic_level = 0
    
    def parse_mermaid(self, mermaid):
        mermaid_topics = []
        mermaid_lines_array = mermaid.split(line_separator)
        if len(mermaid_lines_array) > 1:
            for mermaid_line in mermaid_lines_array[1:]:
                if mermaid_line.strip():
                    indent_level = (len(mermaid_line) - len(mermaid_line.lstrip())) // indent_size
                    mermaid_topic = MermaidTopic(mermaid_line.strip(), indent_level - 1)
                    mermaid_topics.append(mermaid_topic)
        return mermaid_topics

    def export_to_markmap(self):
        max_topic_level = 1
        lines = self.mermaid_mindmap.split(line_separator)
        for i in range(1, len(lines)):
            level = (len(lines[i]) - len(lines[i].lstrip())) // indent_size
            if level > max_topic_level:
                max_topic_level = level
            if i < len(lines) - 1:
                next_level = (len(lines[i+1]) - len(lines[i+1].lstrip())) // indent_size
                if next_level > level:
                    lines[i] = "#" * int(level) + " " + lines[i].lstrip()
                else:
                    lines[i] = "- " + lines[i].lstrip()
            else:
                lines[i] = "#" * int(level) + " " + lines[i].lstrip()
        return line_separator.join(lines[1:]), max_topic_level - 1

    def export_to_mermaid(self, replacements=True):
        mermaid = self.mermaid_mindmap
        if replacements:
            mermaid = mermaid \
                        .replace("(", "#40;").replace(")", "#41;") \
                        .replace("{", "#123;").replace("}", "#125;") \
                        .replace("[", "#91;").replace("]", "#93;")
        max_topic_level = 1
        lines = mermaid.split(line_separator)
        for i in range(1, len(lines)):
            level = (len(lines[i]) - len(lines[i].lstrip())) // indent_size
            if level > max_topic_level:
                max_topic_level = level
            if i < len(lines) - 1:
                next_level = (len(lines[i+1]) - len(lines[i+1].lstrip())) // indent_size
                if next_level > level:
                    lines[i] = " " * indent_size * int(level) + "(" + lines[i].lstrip() + ")"
                else:
                    lines[i] = " " * indent_size * int(level) + lines[i].lstrip()
            else:
                if len(lines[i].strip()) > 0:
                    lines[i] = " " * indent_size * int(level) + "(" + lines[i].lstrip() + ")"
        return line_separator.join(lines), max_topic_level - 1

    def create_sub_topics(self, mermaid_topics, index, parent_topic): # MindmapTopic
        i = index
        parent_topic_level = parent_topic.topic_level
        last_topic = None
        while i < len(mermaid_topics):
            topic_level = mermaid_topics[i].topic_level
            topic_text = mermaid_topics[i].topic_text
            if topic_level <= parent_topic_level: 
                return i
            if topic_level == parent_topic_level + 1:
                new_topic = MindmapTopic(topic_text=topic_text, topic_level=topic_level, topic_subtopics=[])
                parent_topic.topic_subtopics.append(new_topic)
                last_topic = new_topic
            if topic_level > parent_topic_level + 1:
                i = self.create_sub_topics(mermaid_topics, i, last_topic) - 1
            i += 1
        return i

    def create_mindmap_from_mermaid(self):
        mermaid_topics = self.mermaid_topics
        parent_topic = MindmapTopic(topic_text=mermaid_topics[0].topic_text, topic_level=0)
        self.create_sub_topics(mermaid_topics, 1, parent_topic)
        return parent_topic

def get_root(): return "root" if use_root and use_round else ""
def get_left_round(): return "(" if use_round else ""
def get_right_round(): return ")" if use_round else ""
def get_space_string(level): return ' ' * level * indent_size

def validate_mermaid(mermaid_mindmap):
    pattern_text = r"^(?:\s{" + str(indent_size) + r"})*\S.*"
    pattern = re.compile(pattern_text, re.MULTILINE)
    matches = pattern.findall(mermaid_mindmap)
    non_empty_lines = [line for line in mermaid_mindmap.split(line_separator) if line.strip() and not line.strip().startswith('//')]
    if len(matches) == len(non_empty_lines):
        return False  # All lines match the pattern
    else:
        return True  # Some lines do not match the pattern

def get_mermaid_line(level, topic):
    if level == 0:
        return (
            f"mindmap{line_separator}"
            f"{get_space_string(1)}{get_root()}{get_left_round()}{topic}{get_right_round()}{line_separator}"
        )
    if level > 1:
        return f"{get_space_string(level)}{get_left_round()}{topic}{get_right_round()}{line_separator}"

def get_mermaid_from_mindmap(mindmap):
    return recurse_topics("", mindmap, 0)

def recurse_topics(mermaid_mindmap, this_topic, level):
    this_topic_text = this_topic.topic_text
    if level == 0:
        top_level = get_mermaid_line(0, this_topic_text)
        mermaid_mindmap = recurse_topics(top_level, this_topic, 1)
        return mermaid_mindmap
    if level > 1:
        mermaid_mindmap += get_mermaid_line(level, this_topic_text)
    for child_topic in this_topic.topic_subtopics:
        mermaid_mindmap = recurse_topics(mermaid_mindmap, child_topic, level + 1)
    return mermaid_mindmap
