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
            if attr_name in ["topic_rtf"]:
                continue
            #if attr_name == "topic_rtf" and hasattr(obj, 'topic_text') and obj.topic_text == attr_value:
            #    continue
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


def escape_mermaid_text(text: str) -> str:
    """
    Escapes special characters for the Mermaid node text (which is output outside JSON)
    and then replaces non-ASCII characters with HTML entities.
    """
    if not isinstance(text, str):
        return text
    # Escape backslashes, newlines, carriage returns, and double quotes.
    escaped = text.replace("\\", "\\\\") \
                  .replace("\n", "\\n") \
                  .replace("\r", "") \
                  .replace("\"", "\\\"")
    # Replace any non-ASCII characters with HTML entities.
    return replace_unicode_for_markdown(escaped)

def replace_unicode_for_markdown(text: str) -> str:
    """
    For a given text string, replaces every non-ASCII character with its HTML entity.
    For example, 'é' becomes '&#233;'.
    """
    return ''.join(ch if ord(ch) < 128 else f'&#{ord(ch)};' for ch in text)

def replace_unicode_in_obj(obj):
    """
    Recursively traverse an object (dict, list, or string) and replace non-ASCII characters 
    in any string with their HTML entity.
    """
    if isinstance(obj, str):
        return replace_unicode_for_markdown(obj)
    elif isinstance(obj, list):
        return [replace_unicode_in_obj(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: replace_unicode_in_obj(value) for key, value in obj.items()}
    else:
        return obj

def serialize_attributes(topic, guid_mapping):
    """
    Build a dictionary of all non-empty attributes for a MindmapTopic.
    
    - Replaces topic_guid with an "id" using guid_mapping.
    - Removes the object-specific prefixes (for links, notes, icons, etc.).
    - Applies the guid mapping to any GUIDs in links and references.
    - Suppresses 'rtf' if it is identical to the topic's text.
    - Omits the 'level' and 'parent' attributes.
    
    Before dumping to JSON the dictionary is processed to replace any non-ASCII 
    characters with HTML entities.
    """
    attrs = {}
    # Use the mapped id for the main topic.
    attrs["id"] = guid_mapping.get(topic.topic_guid, topic.topic_guid)
    
    # Add rtf only if it's non-empty and different from topic_text.
    if topic.topic_rtf and topic.topic_rtf != topic.topic_text:
        attrs["rtf"] = topic.topic_rtf

    # Include 'selected' only if True.
    if topic.topic_selected:
        attrs["selected"] = topic.topic_selected
        
    # Process links – remove the "link_" prefix and apply guid mapping to link_guid.
    if topic.topic_links:
        links_list = []
        for link in topic.topic_links:
            link_dict = {}
            if link.link_text:
                link_dict["text"] = link.link_text
            if link.link_url:
                link_dict["url"] = link.link_url
            if link.link_guid:
                mapped = guid_mapping.get(link.link_guid, link.link_guid)
                link_dict["guid"] = mapped
            if link_dict:
                links_list.append(link_dict)
        if links_list:
            attrs["links"] = links_list

    # Process image – remove the "image_" prefix.
    if topic.topic_image and topic.topic_image.image_text:
        attrs["image"] = {"text": topic.topic_image.image_text}
    
    # Process icons – remove the "icon_" prefix.
    if topic.topic_icons:
        icons_list = []
        for icon in topic.topic_icons:
            icon_dict = {}
            if icon.icon_text:
                icon_dict["text"] = icon.icon_text
            icon_dict["is_stock_icon"] = icon.icon_is_stock_icon
            if icon.icon_index:
                icon_dict["index"] = icon.icon_index
            if icon.icon_signature:
                icon_dict["signature"] = icon.icon_signature
            if icon.icon_path:
                icon_dict["path"] = icon.icon_path
            if icon.icon_group:
                icon_dict["group"] = icon.icon_group
            if icon_dict:
                icons_list.append(icon_dict)
        if icons_list:
            attrs["icons"] = icons_list

    # Process notes – remove the "note_" prefix.
    if topic.topic_notes:
        notes_dict = {}
        if isinstance(topic.topic_notes, str):
            if topic.topic_notes:
                notes_dict["text"] = topic.topic_notes
        else:
            if hasattr(topic.topic_notes, 'note_text') and topic.topic_notes.note_text:
                notes_dict["text"] = topic.topic_notes.note_text
            if hasattr(topic.topic_notes, 'note_xhtml') and topic.topic_notes.note_xhtml:
                notes_dict["xhtml"] = topic.topic_notes.note_xhtml
            if hasattr(topic.topic_notes, 'note_rtf') and topic.topic_notes.note_rtf:
                notes_dict["rtf"] = topic.topic_notes.note_rtf
        if notes_dict:
            attrs["notes"] = notes_dict

    # Process tags – remove the "tag_" prefix.
    if topic.topic_tags:
        tags_list = [tag.tag_text for tag in topic.topic_tags if tag.tag_text]
        if tags_list:
            attrs["tags"] = tags_list

    # Process references – remove the "reference_" prefix.
    # Also apply guid mapping to both reference GUIDs.
    if topic.topic_references:
        references_list = []
        for ref in topic.topic_references:
            ref_dict = {}
            if ref.reference_topic_guid_1:
                mapped = guid_mapping.get(ref.reference_topic_guid_1, ref.reference_topic_guid_1)
                ref_dict["guid1"] = mapped
            if ref.reference_topic_guid_2:
                mapped = guid_mapping.get(ref.reference_topic_guid_2, ref.reference_topic_guid_2)
                ref_dict["guid2"] = mapped
            if ref.reference_direction:
                ref_dict["direction"] = ref.reference_direction
            if ref.reference_label:
                ref_dict["label"] = ref.reference_label
            if ref_dict:
                references_list.append(ref_dict)
        if references_list:
            attrs["references"] = references_list

    # Replace any non-ASCII characters in all string fields.
    attrs = replace_unicode_in_obj(attrs)
    return json.dumps(attrs, ensure_ascii=False)

def serialize_mindmap(root_topic):
    """
    Serializes the full MindmapTopic tree into Mermaid mindmap syntax.
    
    Each node is output on a separate indented line as:
    
      <indent>(<escaped topic_text>) %% <JSON comment with attributes>
    
    The node text is enclosed in parentheses, and the JSON comment (after the %% marker)
    contains all non-empty attributes (with object-specific prefixes removed and any GUID
    replaced by its mapped integer).
    """
    # Build a mapping: topic_guid -> unique integer (starting at 1)
    guid_mapping = {}
    next_id = 1
    def build_mapping(topic):
        nonlocal next_id
        if topic.topic_guid not in guid_mapping:
            guid_mapping[topic.topic_guid] = next_id
            next_id += 1
        for sub in topic.topic_subtopics:
            build_mapping(sub)
    build_mapping(root_topic)
    
    lines = ["mindmap"]
    def traverse(topic, indent):
        indent_str = "  " * indent  # two spaces per level
        # Escape and convert Unicode in the topic text.
        node_text = escape_mermaid_text(topic.topic_text)
        # Enclose the node text in parentheses.
        line = f"{indent_str}({node_text})"
        # Build the JSON comment with all non-empty attributes.
        attrs_comment = serialize_attributes(topic, guid_mapping)
        if attrs_comment and attrs_comment != "{}":
            line += f" %% {attrs_comment}"
        lines.append(line)
        for sub in topic.topic_subtopics:
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
