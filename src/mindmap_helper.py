class MindmapLink:
    def __init__(self, link_text: str = '', link_url: str = ''):
        self.link_text = link_text
        self.link_url = link_url

class MindmapImage:
    def __init__(self, image_text: str = ''):
        self.image_text = image_text

class MindmapNotes:
    def __init__(self, note_text: str = ''):
        self.note_text = note_text

class MindmapIcon:
    def __init__(self, icon_text: str = '', icon_index: int = 1): # 1=unknown
        self.icon_text = icon_text,
        self.icon_index = icon_index

class MindmapTag:
    def __init__(self, tag_text: str = ''):
        self.tag_text = tag_text

class MindmapReference:
    def __init__(self, reference_object1: str = '', reference_object2: str = '', reference_direction: str = '', reference_label: str = ''):
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
                 topic_image: str = None, # ok
                 topic_icons: list['MindmapIcon'] = [], # ok
                 topic_notes: 'MindmapNotes' = None, # ok
                 topic_tags: list['MindmapTag'] = [], 
                 topic_references: list['MindmapReference'] = [] # ok
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

class MindMapGuidMap:
    def __init__(self, guid: str = '', original_guid: str = ''):
        self.guid = guid
        self.original_guid = original_guid