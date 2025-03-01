import re
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mindm.mindmap_helper import MindmapTopic

INDENT_SIZE = 2
LINE_SEPARATOR = "\n"

line_separator = LINE_SEPARATOR
indent_size = INDENT_SIZE
use_round = False
use_root = True

class MermaidTopic:
    def __init__(self, text='', level=0):
        self.text = text
        self.level = level

class MermaidMindmap:
    def __init__(self, mermaid_mindmap: str=''):
        self.mermaid_mindmap = mermaid_mindmap

        if self.mermaid_mindmap:
            if validate_mermaid(mermaid_mindmap):
                raise ValueError("The Mermaid mindmap is not valid.")
            self.mermaid_topics: list['MermaidTopic'] = self.parse_mermaid(mermaid_mindmap)
            self.max_topic_level: int = max(topic.level for topic in self.mermaid_topics)
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

    def create_mindmap_from_mermaid(self) -> MindmapTopic:
        mindmap_nodes = [MindmapTopic(text=mt.text, level=mt.level) for mt in self.mermaid_topics]
        root = mindmap_nodes[0]
        for i in range(1, len(mindmap_nodes)):
            curr_node = mindmap_nodes[i]
            prev_node = mindmap_nodes[i - 1]
            if curr_node.level > prev_node.level:
                curr_node.parent = prev_node
                prev_node.subtopics.append(curr_node)
            elif curr_node.level == prev_node.level:
                parent = prev_node.parent
                curr_node.parent = parent
                if parent:
                    parent.subtopics.append(curr_node)
            else:
                target_level = curr_node.level - 1
                j = i - 1
                while j >= 0 and mindmap_nodes[j].level != target_level:
                    j -= 1
                if j >= 0:
                    parent = mindmap_nodes[j]
                    curr_node.parent = parent
                    parent.subtopics.append(curr_node)
        return root

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

def get_mermaid_from_mindmap(mindmap):

    def get_mermaid_line(level, topic):
        if level == 0:
            return (
                f"mindmap{line_separator}"
                f"{get_space_string(1)}{get_root()}{get_left_round()}{topic}{get_right_round()}{line_separator}"
            )
        if level > 1:
            return f"{get_space_string(level)}{get_left_round()}{topic}{get_right_round()}{line_separator}"

    def recurse_topics(mermaid_mindmap, this_topic, level):
        this_topic_text = this_topic.text
        if level == 0:
            top_level = get_mermaid_line(0, this_topic_text)
            mermaid_mindmap = recurse_topics(top_level, this_topic, 1)
            return mermaid_mindmap
        if level > 1:
            mermaid_mindmap += get_mermaid_line(level, this_topic_text)
        for child_topic in this_topic.subtopics:
            mermaid_mindmap = recurse_topics(mermaid_mindmap, child_topic, level + 1)
        return mermaid_mindmap
    return recurse_topics("", mindmap, 0)
