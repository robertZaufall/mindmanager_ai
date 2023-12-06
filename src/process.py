#!/usr/bin/env python3
import config
import prompts
import llm
import mermaid
import sys

if sys.platform.startswith('win'):
    import mindmanager_win as mindmanager
elif sys.platform.startswith('darwin'):
    import mindmanager_mac as mindmanager

def recurse_topics(mindm, mermaid_diagram, this_topic, level):
    this_topic_text = mindm.get_title_from_topic(this_topic)
    
    if level == 0:
        top_level = mermaid.get_mermaid_line(0, this_topic_text)
        mermaid_diagram = recurse_topics(mindm, top_level, this_topic, 1)
        return mermaid_diagram

    if level > 1:
        mermaid_diagram += mermaid.get_mermaid_line(level, this_topic_text)

    for child_topic in mindm.get_subtopics_from_topic(this_topic):
        mermaid_diagram = recurse_topics(mindm, mermaid_diagram, child_topic, level + 1)
    
    return mermaid_diagram

def create_sub_topics(mindm, mermaid_topics, index, parent_topic):
    i = index
    parent_topic_level = mindm.get_level_from_topic(parent_topic)

    last_topic = None
    while i < len(mermaid_topics):
        topic_level = mermaid_topics[i].topic_level
        topic_text = mermaid_topics[i].topic_text

        if topic_level <= parent_topic_level: return i

        if topic_level == parent_topic_level + 1:
            new_topic = mindm.add_subtopic_to_topic(parent_topic, topic_text)
            last_topic = new_topic

        if topic_level > parent_topic_level + 1:
            i = create_sub_topics(mindm, mermaid_topics, i, last_topic) - 1

        i += 1
    return i

def create_new_map_from_mermaid(mindm, mermaid_diagram):
    mermaid_topics = mermaid.parse_mermaid(mermaid_diagram, config.LINE_SEPARATOR, config.INDENT_SIZE)
    mindm.add_document()
    parent_topic = mindm.get_central_topic()
    mindm.set_title_to_topic(parent_topic, mermaid_topics[0].topic_text)
    create_sub_topics(mindm, mermaid_topics, 1, mindm.get_central_topic())



def main(param):
    mindm = mindmanager.Mindmanager()
    
    prompts_list = prompts.prompts_list_from_param(param)

    if mindm.document_exists():
        topic_texts = ""

        central_topic = mindm.get_central_topic()
        mermaid_diagram = recurse_topics(mindm, "", central_topic, 0)

        if len(prompts_list) == 1:
            selection = mindm.get_selection()
            if len(selection) > 0:
                for this_topic in selection:
                    if mindm.get_level_from_topic(this_topic) > 0:
                        topic_texts += mindm.get_title_from_topic(this_topic) + ","
                    
                if len(topic_texts) > 0: topic_texts = topic_texts[:-1]

        new_mermaid_diagram = llm.call_llm_sequence(prompts_list, mermaid_diagram, topic_texts)

        if new_mermaid_diagram != "": create_new_map_from_mermaid(mindm, new_mermaid_diagram)
        mindm.finalize()

        print("Done.")
    else:
        print("No document found.")

if __name__ == "__main__":
    
    param = "refine"
    
    if len(sys.argv) > 1:
        param = sys.argv[1]
        
    try:
        main(param)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
