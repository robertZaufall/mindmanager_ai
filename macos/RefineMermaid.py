#!/usr/bin/env python3
import sys

import config
import json
import requests
import os

from appscript import *

use_round = False
use_root = True
indent_size = 2
line_separator = "\n"

current_folder = os.getcwd()

class MermaidTopic:
    def __init__(self, topic_text='', topic_level=0):
        self.topic_text = topic_text
        self.topic_level = topic_level

def get_root():
    return "root" if use_root and use_round else ""

def get_left_round():
    return "(" if use_round else ""

def get_right_round():
    return ")" if use_round else ""

def get_space_string(level):
    return ' ' * level * indent_size

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
        topic_level = mermaid_topics[i].topic_level
        topic_text = mermaid_topics[i].topic_text

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

def recurse_topics(mermaid_diagram, this_topic, level):
    current_level = level
    this_topic_text = this_topic.title.get()
    
    if current_level == 0:
        top_level = f"mindmap{line_separator}{get_space_string(1)}{get_root()}{get_left_round()}{this_topic_text}{get_right_round()}{line_separator}"
        mermaid_diagram = recurse_topics(top_level, this_topic, 1)
        return mermaid_diagram

    if current_level > 1:
        mermaid_diagram += f"{get_space_string(current_level)}{get_left_round()}{this_topic_text}{get_right_round()}{line_separator}"

    for child_topic in this_topic.subtopics.get():
        mermaid_diagram = recurse_topics(mermaid_diagram, child_topic, current_level + 1)
    
    return mermaid_diagram

def prompt_refine():
    str_user = ("Given is the following Mermaid mindmap. Please refine each subtopic by adding a new level with "
                "top " + str(config.TOP_MOST_RESULTS) + " most important subtopics, "
                "if you decide from your knowledge there have to be more or less most important subtopics you can increase or decrease this number, "
                "with each subtopic " + str(config.MAX_RETURN_WORDS) + " words at maximum, "
                "and return the same Mermaid structure back with two spaces as indentation and no additional text: \n")
    return str_user

def call_llm(mermaid, str_user):
    str_system = "You are a business consultant and helpful assistant."
    str_user += mermaid.replace("\r", "\n")

    payload = {
        "max_tokens": config.MAX_TOKENS_DEEP,
        "temperature": config.OPENAI_TEMPERATURE,
        "messages": [
            {"role": "system", "content": str_system},
            {"role": "user", "content": str_user}
        ]
    }
    if config.CLOUD_TYPE == "OPENAI":
        payload["model"] = config.OPENAI_MODEL

    response = requests.post(
        config.API_URL,
        headers={
            "Content-Type": "application/json",
            config.KEY_HEADER_TEXT: config.KEY_HEADER_VALUE
        },
        data=json.dumps(payload)
    )
    response_text = response.text

    parsed_json = json.loads(response_text)
    result = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "").lstrip("\n")
    
    return result

def map_from_mermaid(mindmanager, new_mermaid):
    mindmanager.documents.end.make(new=k.document)

    new_central_topic_ref = mindmanager.documents[1].central_topic
    new_central_topic = new_central_topic_ref.get()

    mermaid_topics = parse_mermaid(new_mermaid)

    new_central_topic.title.set(mermaid_topics[0].topic_text)

    i = create_sub_topics(mermaid_topics, 1, new_central_topic_ref)

def main():
    mindmanager = app('MindManager')

    if mindmanager.documents[1].exists():

        # use selection if available
        #selection = mindmanager.documents[1].selection.get()
        #if selection != {}:
        #
        #else:
        #    print("No topic node selected.")

        # use central topic
        central_topic = mindmanager.documents[1].central_topic.get()

        # get mindmap in mermaid syntax
        mermaid = recurse_topics("", central_topic, 0)

        # get LLM response
        new_mermaid = call_llm(mermaid, prompt_refine())

        # create new document
        map_from_mermaid(mindmanager, new_mermaid)

        mindmanager.documents[1].balance_map()
        mindmanager.activate()

        print("Done.")

    else:
        print("No document found.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
