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
            if attr_name in ["parent", "level", "selected"]:
                continue
            if attr_name in ["rtf"]:
                continue
            if attr_value == None or attr_value == "" or attr_value == []:
                continue
            new_attr_name = attr_name
            
            # Handle GUID replacement
            if new_attr_name in ["guid", "guid_1", "guid_2"]:
                if new_attr_name == "guid":
                    new_attr_name = "id"
                elif new_attr_name == "guid_1":
                    new_attr_name = "id_1"
                elif new_attr_name == "guid_2":
                    new_attr_name = "id_2"
                if attr_value not in guid_mapping:
                    guid_mapping[attr_value] = len(guid_mapping) + 1
                serialized[new_attr_name] = guid_mapping[attr_value]
            else:
                serialized[new_attr_name] = serialize_object(attr_value, guid_mapping, visited)
        return serialized

    return str(obj)


def escape_mermaid_text(text: str) -> str:
    r"""
    Escapes special characters for the Mermaid node text (output outside JSON)
    and converts every non-ASCII character to its Unicode escape sequence.
    
    For example, if the input is:
    
        ThisÂ  is a Â test\n
    
    it becomes:
    
        This\u00c2\u00a0 is a \u00c2\u00a0test\n
    """
    if not isinstance(text, str):
        return text
    # First, escape backslashes, newlines, carriage returns, and double quotes.
    escaped = text.replace("\\", "\\\\") \
                  .replace("\n", "\\n") \
                  .replace("\r", "") \
                  .replace("\"", "\\\"")
    result = []
    for ch in escaped:
        if ord(ch) > 127:
            # Convert non-ASCII character to its \uXXXX escape sequence.
            result.append("\\u{:04x}".format(ord(ch)))
        else:
            result.append(ch)
    return "".join(result)

def replace_unicode_for_markdown(text: str) -> str:
    """
    Previously this function converted non-ASCII characters to HTML entities.
    Now it simply returns the text unchanged so that characters like umlauts
    are preserved.
    """
    return text

def replace_unicode_in_obj(obj):
    """
    Recursively traverses an object (dict, list, or string) and processes any string 
    using replace_unicode_for_markdown (which now is a no-op, preserving Unicode characters).
    """
    if isinstance(obj, str):
        return replace_unicode_for_markdown(obj)
    elif isinstance(obj, list):
        return [replace_unicode_in_obj(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: replace_unicode_in_obj(value) for key, value in obj.items()}
    else:
        return obj

def serialize_topic_attributes(topic, guid_mapping):
    """
    Build a dictionary containing every attribute of the topic except 'parent' and 'level',
    renaming 'guid' to 'id'. For sub-objects (links, image, icons, notes, tags, references),
    their own guid attributes are also mapped/renamed.
    """
    d = {}
    # Rename topic.guid -> id.
    d["id"] = guid_mapping.get(topic.guid, topic.guid)
    # Include text, rtf, and selected.
    d["text"] = topic.text
    d["rtf"] = topic.rtf
    d["selected"] = topic.selected

    # Process links.
    if topic.links:
        d["links"] = []
        for link in topic.links:
            l = {
                "text": link.text,
                "url": link.url
            }
            if link.guid:
                l["id"] = guid_mapping.get(link.guid, link.guid)
            d["links"].append(l)

    # Process image.
    if topic.image:
        d["image"] = {"text": topic.image.text}

    # Process icons.
    if topic.icons:
        d["icons"] = []
        for icon in topic.icons:
            i = {
                "text": icon.text,
                "is_stock_icon": icon.is_stock_icon,
                "index": icon.index,
                "signature": icon.signature,
                "path": icon.path,
                "group": icon.group
            }
            d["icons"].append(i)

    # Process notes.
    if topic.notes:
        if isinstance(topic.notes, str):
            d["notes"] = {"text": topic.notes}
        else:
            d["notes"] = {
                "text": topic.notes.text,
                "xhtml": topic.notes.xhtml,
                "rtf": topic.notes.rtf
            }

    # Process tags.
    if topic.tags:
        d["tags"] = [tag.text for tag in topic.tags]

    # Process references.
    if topic.references:
        d["references"] = []
        for ref in topic.references:
            r = {}
            if ref.guid_1:
                r["id1"] = guid_mapping.get(ref.guid_1, ref.guid_1)
            if ref.guid_2:
                r["id2"] = guid_mapping.get(ref.guid_2, ref.guid_2)
            r["direction"] = ref.direction
            r["label"] = ref.label
            d["references"].append(r)

    # Process all string fields for Unicode replacement (now a no-op).
    d = replace_unicode_in_obj(d)
    return d

def serialize_mindmap(root_topic):
    """
    Serializes the full MindmapTopic tree into Mermaid mindmap syntax.
    
    Each node is output on a separate indented line as:
    
      <indent>(<escaped topic.text>) %% <JSON comment with topic attributes>
    
    The JSON comment (after the %% marker) contains every attribute (except 'parent'
    and 'level') with 'guid' renamed to 'id'.
    """
    # Build a mapping: topic.guid -> unique integer (starting at 1)
    guid_mapping = {}
    next_id = 1
    def build_mapping(topic):
        nonlocal next_id
        if topic.guid not in guid_mapping:
            guid_mapping[topic.guid] = next_id
            next_id += 1
        for sub in topic.subtopics:
            build_mapping(sub)
    build_mapping(root_topic)
    
    lines = ["mindmap"]
    def traverse(topic, indent):
        indent_str = "  " * indent  # two spaces per level
        # Escape and process Unicode in the topic text.
        node_text = escape_mermaid_text(topic.text)
        # Enclose the topic text in parentheses.
        line = f"{indent_str}({node_text})"
        # Serialize the topic's attributes as JSON for the comment.
        topic_attrs = serialize_topic_attributes(topic, guid_mapping)
        # Use ensure_ascii=True so that non-ASCII characters appear as \uXXXX escapes.
        json_comment = json.dumps(topic_attrs, ensure_ascii=True)
        line += f" %% {json_comment}"
        lines.append(line)
        for sub in topic.subtopics:
            traverse(sub, indent + 1)
    traverse(root_topic, 1)
    
    return "\n".join(lines)

def serialize_graph_to_json(root):
    guid_mapping = {}
    data = serialize_object(root, guid_mapping)
    return json.dumps(data, indent=1)

def serialize_graph_to_yaml(root):
    guid_mapping = {}
    data = serialize_object(root, guid_mapping)
    return yaml.dump(data, sort_keys=False)

def serialize_graph_mermaid(root):
    data = serialize_mindmap(root)
    return data

def main():
    document = mindmap_helper.MindmapDocument(charttype="auto")
    document.get_mindmap()
    print(serialize_graph_to_json(document.mindmap))
    print(serialize_graph_to_yaml(document.mindmap))
    print(serialize_graph_mermaid(document.mindmap))
    return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise e
