#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mindmap.mindmap_helper import *

def create_mindmap(mindm, mindmap, map_icons):
    mindm.add_document(0)
    mindm.create_map_icons(map_icons)
    topic = mindm.get_central_topic()
    set_topic_from_mindmap_topic(mindm, topic, mindmap, map_icons)

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

    map_icons = []
    mindmap = get_mindmap(mindm)
    create_mindmap(mindm, mindmap, map_icons)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
