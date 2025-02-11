import sys
import os
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.mindmap.mindmap_helper as mindmap_helper

import json
from collections import deque

def serialize_object(obj, guid_mapping, visited=None):
    if visited is None:
        visited = set()

    if id(obj) in visited:
        return None  # Avoid recursion

    visited.add(id(obj))

    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj

    if isinstance(obj, list):
        return [serialize_object(item, guid_mapping, visited) for item in obj]

    if isinstance(obj, dict):
        return {str(k): serialize_object(v, guid_mapping, visited) for k, v in obj.items()}

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
            
            # Handle GUID replacement
            if new_attr_name in ["guid", "reference_guid_1", "reference_guid_2", "link_guid"]:
                if new_attr_name == "guid":
                    new_attr_name = "id"
                elif new_attr_name == "reference_guid_1":
                    new_attr_name = "reference_id_1"
                elif new_attr_name == "reference_guid_2":
                    new_attr_name = "reference_id_2"
                elif new_attr_name == "link_guid":
                    new_attr_name = "link_id"
                if attr_value not in guid_mapping:
                    guid_mapping[attr_value] = len(guid_mapping) + 1
                serialized[new_attr_name] = guid_mapping[attr_value]
            else:
                serialized[new_attr_name] = serialize_object(attr_value, guid_mapping, visited)
        return serialized

    return str(obj)

def serialize_graph_to_json(root):
    guid_mapping = {}
    data = serialize_object(root, guid_mapping)
    return json.dumps(data, indent=1)

def serialize_graph_to_yaml(root):
    guid_mapping = {}
    data = serialize_object(root, guid_mapping)
    return yaml.dump(data)

def main():
    document = mindmap_helper.MindmapDocument(charttype="auto")
    document.get_mindmap()
    print(serialize_graph_to_json(document.mindmap))
    print(serialize_graph_to_yaml(document.mindmap))
    return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise e
