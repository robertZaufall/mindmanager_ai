import sys
import os

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
                 topic_guid: str = '',
                 topic_originalguid: str = '',
                 topic_text: str = '',
                 topic_rtf: str = '',
                 topic_level: int = 0,
                 topic_selected: bool = False,
                 topic_parent: 'MindmapTopic' = None,
                 topic_subtopics: list['MindmapTopic'] = None,
                 topic_link: 'MindmapLink' = None,
                 topic_image: 'MindmapImage' = None,
                 topic_icons: list['MindmapIcon'] = None,
                 topic_notes: 'MindmapNotes' = None,
                 topic_tags: list['MindmapTag'] = None,
                 topic_references: list['MindmapReference'] = None,
                 topic_attributes: list['MindmapAttribute'] = None):
        self.topic_guid = topic_guid
        self.topic_originalguid = topic_originalguid
        self.topic_text = topic_text
        self.topic_rtf = topic_rtf
        self.topic_level = topic_level
        self.topic_selected = topic_selected
        self.topic_parent = topic_parent
        self.topic_subtopics = topic_subtopics if topic_subtopics is not None else []
        self.topic_link = topic_link
        self.topic_image = topic_image
        self.topic_icons = topic_icons if topic_icons is not None else []
        self.topic_notes = topic_notes
        self.topic_tags = topic_tags if topic_tags is not None else []
        self.topic_references = topic_references if topic_references is not None else []
        self.topic_attributes = topic_attributes if topic_attributes is not None else [MindmapAttribute(attribute_name='id')]

class MindmapDocument:

    def __init__(self, charttype: str = 'auto', turbo_mode: bool = False):
        self.charttype: str = charttype
        self.turbo_mode: bool = turbo_mode

        self.mindmap: 'MindmapTopic' = None
        self.map_icons: list['MindmapIcon'] = []
        self.guid_map: dict[str, str] = {}
        self.selection: list['MindmapTopic'] = []
        self.relationships: list['MindmapReference'] = []
        self.central_topic_selected: bool = False
        self.selected_topic_texts: list[str] = []
        self.selected_topic_levels: list[int] = []
        self.max_topic_level: int = 0

        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        if sys.platform.startswith('win'):
            import mindmanager.mindmanager_win as mindmanager
            platform = "win"
        elif sys.platform.startswith('darwin'):
            import mindmanager.mindmanager_mac as mindmanager
            platform = "darwin"

        self.mindm = mindmanager.Mindmanager(charttype)

    def get_mindmap(self, topic=None, attributes_template=[MindmapAttribute(attribute_name='id')]):
        if not self.mindm.document_exists():
            print("No document found.")    
            return False

        if topic is None:
            topic = self.mindm.get_central_topic()
        
        mindmap = self.get_mindmap_topic_from_topic(topic, attributes_template=attributes_template)

        #relationships = []
        #self.get_relationships_from_mindmap(mindmap, relationships)
        #self.relationships = relationships

        #guid_map = {}
        #self.get_guid_map(mindmap, guid_map)
        #self.guid_map = guid_map

        selection = self.get_selection()
        selected_topic_texts, selected_topic_levels, central_topic_selected = self.get_topic_texts_from_selection(selection)
        self.selection = selection

        self.central_topic_selected = central_topic_selected
        self.selected_topic_texts = selected_topic_texts
        self.selected_topic_levels = selected_topic_levels
        self.max_topic_level = self.get_max_topic_level(mindmap)
        self.mindmap = mindmap

        return True

    def get_max_topic_level(self, mindmap_topic, max_topic_level = 0):
        for mindmap_subtopic in mindmap_topic.topic_subtopics:
            if mindmap_subtopic.topic_level > max_topic_level:
                max_topic_level = mindmap_subtopic.topic_level
            max_topic_level = self.get_max_topic_level(mindmap_subtopic, max_topic_level)
        return max_topic_level

    def get_selection(self):
        selection = self.mindm.get_selection()
        mindmap_topics = []
        for topic in selection:
            mindmap_topic = MindmapTopic(
                topic_guid=self.mindm.get_guid_from_topic(topic),
                topic_text=self.mindm.get_text_from_topic(topic), 
                topic_level=self.mindm.get_level_from_topic(topic),
                topic_selected=True,
            )
            mindmap_topics.append(mindmap_topic)
        return mindmap_topics

    def get_mindmap_topic_from_topic(self, topic, parent_topic=None, attributes_template=[]):
        mindmap_topic = MindmapTopic(
            topic_guid=self.mindm.get_guid_from_topic(topic),
            topic_text=self.mindm.get_text_from_topic(topic),
            topic_rtf=self.mindm.get_title_from_topic(topic),
            topic_level=self.mindm.get_level_from_topic(topic),
            topic_link=self.mindm.get_link_from_topic(topic),
            topic_image=self.mindm.get_image_from_topic(topic),
            topic_icons=self.mindm.get_icons_from_topic(topic),
            topic_notes=self.mindm.get_notes_from_topic(topic),
            topic_tags=self.mindm.get_tags_from_topic(topic),
            topic_references=self.mindm.get_references_from_topic(topic),
            topic_parent=parent_topic,
            topic_attributes=self.mindm.get_attributes_from_topic(topic, attributes_template),
        )

        subtopics = self.mindm.get_subtopics_from_topic(topic)
        mindmap_subtopics = []

        for subtopic in subtopics:
            mindmap_subtopic = self.get_mindmap_topic_from_topic(subtopic, mindmap_topic, attributes_template)
            mindmap_subtopics.append(mindmap_subtopic)

        mindmap_topic.topic_subtopics = mindmap_subtopics
        return mindmap_topic 

    def get_relationships_from_mindmap(self, mindmap, references):
        for reference in mindmap.topic_references:
            if reference.reference_direction == 'OUT':
                references.append(reference)
                
        for mindmap_subtopic in mindmap.topic_subtopics:
            self.get_relationships_from_mindmap(mindmap_subtopic, references)

    def get_guid_from_originalguid(self, mindmap, original_guid):
        if mindmap.topic_originalguid == original_guid:
            return mindmap.topic_guid

        for mindmap_subtopic in mindmap.topic_subtopics:
            guid = self.get_guid_from_originalguid(mindmap_subtopic, original_guid)
            if guid:
                return guid
        return None

    def get_guid_map(self, mindmap, guid_map = {}):
        if mindmap.topic_originalguid:
            if mindmap.topic_originalguid != '':
                guid_map[mindmap.topic_originalguid] = mindmap.topic_guid
        else:
            pass
        for mindmap_subtopic in mindmap.topic_subtopics:
            self.get_guid_map(mindmap_subtopic, guid_map)

    def get_attribute_from_mindmap_topic(self, attributes, attribute_name, attribute_namespace='mindmanager.ai'):
        for attribute in attributes:
            if attribute.attribute_name == attribute_name and attribute.attribute_namespace == attribute_namespace:
                return attribute.attribute_value
        return None

    def get_topic_texts_from_selection(self, mindmap_topics):
        topic_texts = []
        topic_levels = []
        central_topic_selected = False
        for mindmap_topic in mindmap_topics:
            if mindmap_topic.topic_selected:
                if mindmap_topic.topic_level > 0:
                    topic_texts.append(mindmap_topic.topic_text)
                    topic_levels.append(mindmap_topic.topic_level)
                else:
                    central_topic_selected = True
        return topic_texts, topic_levels, central_topic_selected
            
    def clone_mindmap_topic(self, mindmap_topic, subtopics=[], attributes=[], parent=None):
        return MindmapTopic(
            topic_guid=mindmap_topic.topic_guid,
            topic_originalguid=mindmap_topic.topic_originalguid,
            topic_text=mindmap_topic.topic_text, 
            topic_rtf=mindmap_topic.topic_rtf,
            topic_level=mindmap_topic.topic_level,
            topic_parent=parent,
            topic_link=mindmap_topic.topic_link,
            topic_image=mindmap_topic.topic_image,
            topic_icons=mindmap_topic.topic_icons,
            topic_notes=mindmap_topic.topic_notes,
            topic_tags=mindmap_topic.topic_tags,
            topic_references=mindmap_topic.topic_references,
            topic_attributes=attributes,
            topic_subtopics=subtopics
        )

    def create_link_to_parent(self, mindmap_topic, done):
        parent = mindmap_topic.topic_parent
        parent_id = self.get_attribute_from_mindmap_topic(parent.topic_attributes, 'id')
        if parent_id:
            link_from = mindmap_topic.topic_guid
            if parent_id in done:
                link_to = done[parent_id]
                self.mindm.add_relationship(link_from, link_to)

    def set_topic_from_mindmap_topic(self, topic, mindmap_topic, map_icons, done = {}, level=0):
        if self.turbo_mode:
            for mindmap_subtopic in mindmap_topic.topic_subtopics:
                subtopic = self.mindm.add_subtopic_to_topic(topic, mindmap_subtopic.topic_text)
                self.set_topic_from_mindmap_topic(subtopic, mindmap_subtopic, map_icons, done, level+1)
        else:
            topic = self.mindm.set_topic_from_mindmap_topic(topic, mindmap_topic, map_icons)

            if level <= 1:
                done = {}
            elif level >= 2: 
                topic_id = self.get_attribute_from_mindmap_topic(mindmap_topic.topic_attributes, 'id')
                if topic_id:
                    done[topic_id] = topic.guid

            if mindmap_topic.topic_subtopics and len(mindmap_topic.topic_subtopics) > 0:
                mindmap_topic.topic_subtopics.sort(key=lambda subtopic: subtopic.topic_text)
    
            for mindmap_subtopic in mindmap_topic.topic_subtopics:
                subtopic_id = self.get_attribute_from_mindmap_topic(mindmap_subtopic.topic_attributes, 'id')
                if subtopic_id in done:
                    #create_link_to_parent(mindm, mindmap_subtopic, done)
                    cloned_subtopic = self.clone_mindmap_topic(mindmap_subtopic)
                    subtopic = self.mindm.add_subtopic_to_topic(topic, cloned_subtopic.topic_text)
                    self.set_topic_from_mindmap_topic(subtopic, cloned_subtopic, map_icons, done, level+1)
                else:
                    subtopic = self.mindm.add_subtopic_to_topic(topic, mindmap_subtopic.topic_text)
                    self.set_topic_from_mindmap_topic(subtopic, mindmap_subtopic, map_icons, done, level+1)
        return mindmap_topic

    def create_mindmap(self, map_icons):
        self.mindm.add_document(0)
        if not self.turbo_mode:
            self.mindm.create_map_icons(map_icons)
        topic = self.mindm.get_central_topic()
        self.set_topic_from_mindmap_topic(topic=topic, mindmap_topic=self.mindmap, map_icons=map_icons)

        if not self.turbo_mode:
            relationships = []
            self.get_relationships_from_mindmap(self.mindmap, relationships)

            guid_map = {}
            self.get_guid_map(self.mindmap, guid_map)

            self.guid_map = guid_map
            self.relationships = relationships

            for reference in relationships:
                object1_guid = guid_map[reference.reference_object1]
                object2_guid = guid_map[reference.reference_object2]
                if object1_guid and object2_guid:
                    self.mindm.add_relationship(object1_guid, object2_guid, reference.reference_label)

    def create_mindmap_and_finalize(self, map_icons):
        self.create_mindmap(map_icons=map_icons)
        self.finalize()

    def finalize(self):
        if self.max_topic_level == 0:
            self.max_topic_level = self.get_max_topic_level(self.mindmap)
        self.mindm.finalize(self.max_topic_level)
    
    def set_background_image(self, image_path):
        self.mindm.set_document_background_image(image_path)
    
    def get_library_folder(self):
        return self.mindm.library_folder