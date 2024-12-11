#!/usr/bin/env python3

import sys
import mindmap_helper

if sys.platform.startswith('win'):
    import mindmanager_win as mindmanager
    platform = "win"
else:
    raise Exception("Unsupported platform")


def get_mindmap_topic_from_topic(mindm, topic, parent_topic=None):

    mindmap_topic = mindmap_helper.MindmapTopic(
        topic_text=mindm.get_title_from_topic(topic), 
        topic_level=mindm.get_level_from_topic(topic),
        topic_link=mindm.get_link_from_topic(topic),
        topic_image=mindm.get_image_from_topic(topic),
        topic_icons=mindm.get_icons_from_topic(topic),
        topic_notes=mindm.get_notes_from_topic(topic),
        topic_tags=mindm.get_tags_from_topic(topic),
        topic_references=mindm.get_references_from_topic(topic),
        topic_parent=parent_topic
    )

    subtopics = mindm.get_subtopics_from_topic(topic)
    mindmap_subtopics = []

    for subtopic in subtopics:
        mindmap_subtopic = get_mindmap_topic_from_topic(mindm, subtopic, mindmap_topic)
        mindmap_subtopics.append(mindmap_subtopic)

    mindmap_topic.topic_subtopics = mindmap_subtopics

    return mindmap_topic 

def get_mindmap(mindm, topic=None):
    if topic is None:
        topic = mindm.get_central_topic()
    
    mindmap = get_mindmap_topic_from_topic(mindm, topic)

    return (mindmap)

def main(charttype="auto"):
    mindm = mindmanager.Mindmanager(charttype)

    if not mindm.document_exists():
        print("No document found.")    
        return

    mindmap = get_mindmap(mindm)
    print(mindmap.topic_text)


if __name__ == "__main__":
    
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")


