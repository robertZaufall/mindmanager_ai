import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.mindmap.mindmap_helper as mindmap_helper

import json
from collections import deque

def get_object_id(obj):
    guid = getattr(obj, 'topic_guid', None)
    if guid:
        return guid
    return f"ObjID_{id(obj)}"

def flatten_object_graph(root):
    nodes = {}
    visited = set()
    queue = deque([root])
    while queue:
        obj = queue.popleft()
        obj_id = get_object_id(obj)
        if obj_id in visited:
            continue
        visited.add(obj_id)
        serialized = {}
        if hasattr(obj, '__dict__'):
            for attr_name, attr_value in vars(obj).items():
                serialized[attr_name] = _serialize_field(attr_value, queue)
        nodes[obj_id] = serialized
    return {
        "root": get_object_id(root),
        "nodes": nodes
    }

def _serialize_field(value, queue):
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, (list, tuple)):
        return [_serialize_field(item, queue) for item in value]
    if isinstance(value, dict):
        result = {}
        for k, v in value.items():
            result[str(k)] = _serialize_field(v, queue)
        return result
    if hasattr(value, '__dict__'):
        obj_id = get_object_id(value)
        queue.append(value)
        return obj_id
    return str(value)

def serialize_graph_to_json(root):
    data = flatten_object_graph(root)
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
