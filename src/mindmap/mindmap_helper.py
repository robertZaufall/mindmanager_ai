import sys

class MindmapLink:
    def __init__(self, link_text: str = '', link_url: str = ''):
        self.link_text = link_text
        self.link_url = link_url

class MindmapImage:
    def __init__(self, image_text: str = ''):
        self.image_text = image_text

class MindmapNotes:
    def __init__(self, note_text: str = '', note_xhtml: str = '', note_rtf: str = ''):
        self.note_text = note_text
        self.note_xhtml = note_xhtml
        self.note_rtf = note_rtf

class MindmapIcon:
    def __init__(self, 
                 icon_text: str = '', 
                 icon_is_stock_icon = True, 
                 icon_index: int = 1, 
                 icon_signature: str = '', 
                 icon_path: str = "",
                 icon_group = ''):
        self.icon_text = icon_text
        self.icon_is_stock_icon = icon_is_stock_icon
        self.icon_index = icon_index
        self.icon_signature = icon_signature
        self.icon_path = icon_path
        self.icon_group = icon_group

class MindmapAttribute:
    def __init__(self, attribute_namespace: str = 'mindmanager.ai', attribute_name: str = '', attribute_value: str = ''):
        self.attribute_namespace = attribute_namespace
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value

class MindmapTag:
    def __init__(self, tag_text: str = ''):
        self.tag_text = tag_text

class MindmapReference:
    def __init__(self, 
                 reference_object1: str = '', 
                 reference_object2: str = '', 
                 reference_direction: str = '', 
                 reference_label: str = ''):
        self.reference_object1 = reference_object1
        self.reference_object2 = reference_object2
        self.reference_direction = reference_direction
        self.reference_label = reference_label

class MindmapTopic:
    def __init__(self, 
                 topic_guid: str = '', # ok
                 topic_originalguid: str = '', # ok
                 topic_text: str = '', # ok
                 topic_level: int = 0, # ok
                 topic_parent: 'MindmapTopic' = None, # ok 
                 topic_subtopics: list['MindmapTopic'] = [], # ok
                 topic_link: 'MindmapLink' = None, # ok
                 topic_image: 'MindmapImage' = None, # ok
                 topic_icons: list['MindmapIcon'] = [], # ok
                 topic_notes: 'MindmapNotes' = None, # ok
                 topic_tags: list['MindmapTag'] = [], 
                 topic_references: list['MindmapReference'] = [], # ok
                 topic_attributes: list['MindmapAttribute'] = [MindmapAttribute(attribute_name='id')],
                 map_icons: list['MindmapIcon'] = [],
        ):
        self.topic_guid = topic_guid
        self.topic_originalguid = topic_originalguid
        self.topic_text = topic_text
        self.topic_level = topic_level
        self.topic_parent = topic_parent
        self.topic_link = topic_link
        self.topic_image = topic_image
        self.topic_icons = topic_icons
        self.topic_notes = topic_notes
        self.topic_tags = topic_tags
        self.topic_references = topic_references
        self.topic_subtopics = topic_subtopics
        self.topic_attributes = topic_attributes
        self.map_icons = map_icons

class MindMapGuidMap:
    def __init__(self, guid: str = '', original_guid: str = ''):
        self.guid = guid
        self.original_guid = original_guid

if sys.platform.startswith('win'):
    import mindmanager.mindmanager_win as mindmanager
    platform = "win"
elif sys.platform.startswith('darwin'):
    import mindmanager.mindmanager_mac as mindmanager
    platform = "darwin"

def get_mindmap(mindm, topic=None, attributes_template=[MindmapAttribute(attribute_name='id')]):
    if topic is None:
        topic = mindm.get_central_topic()
        mindmap = get_mindmap_topic_from_topic(mindm, topic, attributes_template=attributes_template)
    return (mindmap)

def get_mindmap_topic_from_topic(mindm, topic, parent_topic=None, attributes_template=[]):
    mindmap_topic = MindmapTopic(
        topic_guid=mindm.get_guid_from_topic(topic),
        topic_text=mindm.get_title_from_topic(topic), 
        topic_level=mindm.get_level_from_topic(topic),
        topic_link=mindm.get_link_from_topic(topic),
        topic_image=mindm.get_image_from_topic(topic),
        topic_icons=mindm.get_icons_from_topic(topic),
        topic_notes=mindm.get_notes_from_topic(topic),
        topic_tags=mindm.get_tags_from_topic(topic),
        topic_references=mindm.get_references_from_topic(topic),
        topic_parent=parent_topic,
        topic_attributes=mindm.get_attributes_from_topic(topic, attributes_template),
    )

    subtopics = mindm.get_subtopics_from_topic(topic)
    mindmap_subtopics = []

    for subtopic in subtopics:
        mindmap_subtopic = get_mindmap_topic_from_topic(mindm, subtopic, mindmap_topic, attributes_template)
        mindmap_subtopics.append(mindmap_subtopic)

    mindmap_topic.topic_subtopics = mindmap_subtopics
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

def set_topic_from_mindmap_topic(mindm, topic, mindmap_topic, map_icons):
    mindm.set_topic_from_mindmap_topic(topic, mindmap_topic, map_icons)

    for mindmap_subtopic in mindmap_topic.topic_subtopics:
        subtopic = mindm.add_subtopic_to_topic(topic, mindmap_subtopic.topic_text)
        set_topic_from_mindmap_topic(mindm, subtopic, mindmap_subtopic, map_icons)
    return mindmap_topic
