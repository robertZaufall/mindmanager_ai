#!/usr/bin/env python3

from appscript import *
import os

import random
import string

use_round = False
use_root = True
indent_size = 2
line_separator = "\n"

current_folder = os.getcwd()

class MermaidTopic:
    def __init__(self, topic_text='', topic_level=0):
        self.topic_text = topic_text
        self.topic_level = topic_level

def parse_mermaid(mermaid_syntax, delimiter=line_separator, indent_size=indent_size):
    mermaid_topics = []
    mermaid_lines_array = mermaid_syntax.split(line_separator)

    if len(mermaid_lines_array) > 1:
        for mermaid_line in mermaid_lines_array[1:]:
            if mermaid_line.strip():
                indent_level = (len(mermaid_line) - len(mermaid_line.lstrip())) // indent_size
                mermaid_topic = MermaidTopic(mermaid_line.strip(), indent_level - 1)
                mermaid_topics.append(mermaid_topic)

    return mermaid_topics

def create_sub_topics(mermaid_topics, index, parent_topic_ref):
    i = index
    last_topic = None
    parent_topic = parent_topic_ref.get()

    while i < len(mermaid_topics):
        m_topic = mermaid_topics[i]
        topic_level = m_topic.topic_level
        topic_text = m_topic.topic_text

        parent_topic_level = parent_topic_ref.level.get()
        if topic_level <= parent_topic_level:
            return i

        if topic_level == parent_topic_level + 1:
            new_topic = parent_topic.subtopics.end.make(new=k.topic, with_properties={k.name: topic_text})
            last_topic = new_topic

        if topic_level > parent_topic_level + 1:
            i = create_sub_topics(mermaid_topics, i, last_topic) - 1

        i += 1

    return i

def get_root():
    return "root" if use_root and use_round else ""

def get_left_round():
    return "(" if use_round else ""

def get_right_round():
    return ")" if use_round else ""

def get_space_string(level):
    return ' ' * level * indent_size

def recurse_topics(mermaid_diagram, this_topic, level):
    current_level = level
    this_topic_text = this_topic.title.get()
    
    if current_level == 0:
        top_level = f"mindmap{line_separator}{get_space_string(1)}{get_root()}{get_left_round()}{this_topic_text}{get_right_round()}{line_separator}"
        mermaid_diagram = recurse_topics(top_level, this_topic, 1)
        return mermaid_diagram

    if current_level > 1:
        mermaid_diagram += f"{get_space_string(current_level)}{get_left_round()}{this_topic_text}{get_right_round()}{line_separator}"

    child_topics = this_topic.subtopics.get()

    for child_topic in child_topics:
        mermaid_diagram = recurse_topics(mermaid_diagram, child_topic, current_level + 1)
    
    return mermaid_diagram

mindmanager = app('MindManager')

if mindmanager.documents[1].exists():

    mermaid = ""

    selection = mindmanager.documents[1].selection.get()
    central_topic = mindmanager.documents[1].central_topic.get()

    if selection != {}:
        # get mindmap in mermaid syntax
        mermaid = recurse_topics("", central_topic, 0)

        # OpenAI
        # ToDo: OpenAI API
        new_mermaid = mermaid

        # create new document
        new_document = mindmanager.documents.end.make(new=k.document)
        new_central_topic_ref = mindmanager.documents[1].central_topic
        new_central_topic = new_central_topic_ref.get()

        mermaid_topics = parse_mermaid(new_mermaid)

        new_central_topic.title.set(mermaid_topics[0].topic_text)
        
        i = create_sub_topics(mermaid_topics, 1, new_central_topic_ref)

        mindmanager.activate()
    else:
        print("No topic node selected.")
