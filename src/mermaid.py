import config

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
