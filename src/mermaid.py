import config
import re

class MermaidTopic:
    def __init__(self, topic_text='', topic_level=0):
        self.topic_text = topic_text
        self.topic_level = topic_level

use_round = False
use_root = True
line_separator = config.LINE_SEPARATOR

def get_root(): return "root" if use_root and use_round else ""
def get_left_round(): return "(" if use_round else ""
def get_right_round(): return ")" if use_round else ""
def get_space_string(level): return ' ' * level * config.INDENT_SIZE

def parse_mermaid(mermaid_diagran, delimiter, indent_size):
    mermaid_topics = []
    mermaid_lines_array = mermaid_diagran.split(delimiter)

    if len(mermaid_lines_array) > 1:
        for mermaid_line in mermaid_lines_array[1:]:
            if mermaid_line.strip():
                indent_level = (len(mermaid_line) - len(mermaid_line.lstrip())) // indent_size
                mermaid_topic = MermaidTopic(mermaid_line.strip(), indent_level - 1)
                mermaid_topics.append(mermaid_topic)

    return mermaid_topics

def get_mermaid_line(level, topic):
    if level == 0:
        return (
            f"mindmap{line_separator}"
            f"{get_space_string(1)}{get_root()}{get_left_round()}{topic}{get_right_round()}{line_separator}"
        )

    if level > 1:
        return f"{get_space_string(level)}{get_left_round()}{topic}{get_right_round()}{line_separator}"

def validate_mermaid(mermaid_diagram, line_separator, indent_size):
    pattern_text = "^(?:\s{" + str(indent_size) + "})*\S.*"
    pattern = re.compile(pattern_text, re.MULTILINE)
    matches = pattern.findall(mermaid_diagram)
    non_empty_lines = [line for line in mermaid_diagram.split(line_separator) if line.strip() and not line.strip().startswith('//')]
    if len(matches) == len(non_empty_lines):
        return False  # All lines match the pattern
    else:
        return True  # Some lines do not match the pattern

def export_to_markmap(mermaid_diagram):
    line_separator = config.LINE_SEPARATOR
    indent_size = config.INDENT_SIZE

    if validate_mermaid(mermaid_diagram, line_separator, indent_size):
        return ""

    max_topic_level = 1
    lines = mermaid_diagram.split(line_separator)
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

def export_to_mermaid(mermaid_diagram):
    line_separator = config.LINE_SEPARATOR
    indent_size = config.INDENT_SIZE

    if validate_mermaid(mermaid_diagram, line_separator, indent_size):
        return ""

    mermaid_diagram = mermaid_diagram.replace("(", "#40;").replace(")", "#41;") \
                                     .replace("{", "#123;").replace("}", "#125;") \
                                     .replace("[", "#91;").replace("]", "#93;")

    max_topic_level = 1
    lines = mermaid_diagram.split(line_separator)
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
