import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.mindmap.mindmap_helper as mindmap_helper

import json
from collections import deque

def serialize_object(obj, visited=None):
    if visited is None:
        visited = set()

    if id(obj) in visited:
        return None  # Avoid recursion

    visited.add(id(obj))

    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj

    if isinstance(obj, list):
        return [serialize_object(item, visited) for item in obj]

    if isinstance(obj, dict):
        return {str(k): serialize_object(v, visited) for k, v in obj.items()}

    if hasattr(obj, '__dict__'):
        serialized = {}
        for attr_name, attr_value in vars(obj).items():
            if attr_name in ["topic_parent", "topic_level", "topic_selected", "topic_parent"]:
                continue
            if attr_name == "topic_rtf" and hasattr(obj, 'topic_text') and obj.topic_text == attr_value:
                continue
            if attr_value == None or attr_value == "" or attr_value == []:
                continue
            new_attr_name = attr_name.replace("topic_", "")
            serialized[new_attr_name] = serialize_object(attr_value, visited)
        return serialized

    return str(obj)


def serialize_graph_to_json(root):
    data = serialize_object(root)
    return json.dumps(data, indent=2)


def main():
    document = mindmap_helper.MindmapDocument(charttype="auto")
    document.get_mindmap()
    print(serialize_graph_to_json(document.mindmap))
    return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise e
