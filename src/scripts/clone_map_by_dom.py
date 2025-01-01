#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import mindmap.mindmap_helper as mindmap_helper

def main(charttype="auto"):
    document = mindmap_helper.MindmapDocument(charttype="auto")
    if not document.mindm.document_exists():
        print("No document found.")    
        return

    map_icons = []
    attributes = [mindmap_helper.MindmapAttribute(attribute_name='id'), mindmap_helper.MindmapAttribute(attribute_name='typeId')]
    document.get_mindmap(attributes_template=attributes)
    document.create_mindmap(map_icons)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
