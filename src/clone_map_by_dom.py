#!/usr/bin/env python3

import sys
import mindmap_helper

if sys.platform.startswith('win'):
    import mindmanager_win as mindmanager
    platform = "win"
else:
    raise Exception("Unsupported platform")

def get_mindmap(mindm, topic=None):
    if topic is None:
        topic = mindm.get_central_topic()
    
    mindmap = get_mindmap_topic_from_topic(mindm, topic)

    return (mindmap)

def get_mindmap_topic_from_topic(mindm, topic, parent_topic=None):

    mindmap_topic = mindmap_helper.MindmapTopic(
        topic_guid=mindm.get_guid_from_topic(topic),
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

def set_topic_from_mindmap_topic(mindm, topic, mindmap_topic):
    mindm.set_topic_from_mindmap_topic(topic, mindmap_topic)

    for mindmap_subtopic in mindmap_topic.topic_subtopics:
        subtopic = mindm.add_subtopic_to_topic(topic, mindmap_subtopic.topic_text)
        set_topic_from_mindmap_topic(mindm, subtopic, mindmap_subtopic)

    return mindmap_topic

def get_relationships_from_mindmap(mindmap, references):
    for reference in mindmap.topic_references:
        if reference.reference_direction == 'OUT':
            references.append(reference)

    for mindmap_subtopic in mindmap.topic_subtopics:
        get_relationships_from_mindmap(mindmap_subtopic, references)

def get_guid_from_originalguid(mindmap, original_guid):
    if mindmap.topic_originalguid == original_guid:
        return mindmap.topic_guid

    for mindmap_subtopic in mindmap.topic_subtopics:
        guid = get_guid_from_originalguid(mindmap_subtopic, original_guid)
        if guid:
            return guid

    return None

def create_mindmap(mindm, mindmap):
    mindm.add_document(0)
    topic = mindm.get_central_topic()
    set_topic_from_mindmap_topic(mindm, topic, mindmap)

    references = []
    get_relationships_from_mindmap(mindmap, references)
    for reference in references:
        object1_guid = get_guid_from_originalguid(mindmap, reference.reference_object1)
        object2_guid = get_guid_from_originalguid(mindmap, reference.reference_object2)
        if object1_guid and object2_guid:
            mindm.add_relationship(object1_guid, object2_guid, reference.reference_label)
    return

def main(charttype="auto"):
    mindm = mindmanager.Mindmanager(charttype)

    if not mindm.document_exists():
        print("No document found.")    
        return

    mindmap = get_mindmap(mindm)
    create_mindmap(mindm, mindmap)

    print(mindmap.topic_text)

if __name__ == "__main__":
    
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")


