import os
import sys
from appscript import *
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mindmap.mindmap_helper import MindmapLink, MindmapImage, MindmapNotes, MindmapIcon, MindmapAttribute, MindmapTag, MindmapReference, MindmapTopic

class Mindmanager:

    MACOS_MERGE_ALL_WINDOWS = False
    MACOS_LIBRARY_FOLDER = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Mindjet", "MindManager", "XX", "English", "Library")

    def __init__(self, charttype):
        self.mindmanager = app('MindManager')
        self.master_window = self.mindmanager.windows[1].id.get()
        self.charttype = charttype
        self.library_folder = self.MACOS_LIBRARY_FOLDER.replace("XX", self.mindmanager.version.get().split('.')[0])
        self.orgchart_template = mactypes.Alias(os.path.join(self.library_folder, "Templates", "Blank Templates", "Org-Chart Map.mmat"))
        self.radial_template = mactypes.Alias(os.path.join(self.library_folder, "Templates", "Blank Templates", "Radial Map.mmat"))
    
    def merge_windows(self):
        for window in self.mindmanager.windows():
            if window.id.get() == self.master_window:
                window.activate()
        system_events = app("System Events")
        system_events.processes["MindManager"].menu_bars[1].menu_bar_items["Window"].menus["Window"].menu_items["Merge All Windows"].click()

    def set_document_background_image(self, path):
        pass
    
    def document_exists(self):
        return self.mindmanager.documents[1].exists()

    def get_central_topic(self):
        object = self.mindmanager.documents[1].central_topic.get()
        #callouts = object.callouts.get()
        #relationships = object.relationships.get()
        #subtopics = object.subtopics.get()
        #shape = object.shape.get()
        #attributes = object.attributes.get()
        #props = object.properties.get()
        #task = object.task.get()
        #task_properties = task.properties.get()
        return object
    
    def get_topic_by_id(self, id):
        found_topics = self.mindmanager.documents[1].topics[its.id == id]
        if found_topics.count() == 0:
            return None
        return found_topics[0].get()
    
    def get_selection(self):
        return self.mindmanager.documents[1].selection.get()
    
    def get_level_from_topic(self, topic):
        return topic.level.get()
    
    def get_text_from_topic(self, topic):
        return topic.name.get()
    
    def get_title_from_topic(self, topic):
        return topic.title.get()

    def get_subtopics_from_topic(self, topic):
        return topic.subtopics.get()

    def get_link_from_topic(self, topic) -> MindmapLink:
        return None
        
        # this results in a severe runtime error of MindManager
        link = topic.hyperlink_URL.get()
        if link == k.missing_value:
            link = None
        label = topic.label.get() if link else None
        return MindmapLink(link=link, label=label) if link else None

    def get_image_from_topic(self, topic) -> MindmapImage:
        return None

    def get_icons_from_topic(self, topic) -> list[MindmapIcon]:
        return []

    def get_notes_from_topic(self, topic) -> MindmapNotes:
        return topic.notes.get()

    def get_tags_from_topic(self, topic) -> list[MindmapTag]:
        return []

    def get_references_from_topic(self, topic) -> list[MindmapReference]:
        references = []
        relationships = topic.relationships.get()
        for relationship in relationships:
            relationship_instance = relationship.get()
            starting_location = relationship_instance.starting_location.get()
            ending_location = relationship_instance.ending_location.get()
            if starting_location == topic:
                references.append(MindmapReference(
                    reference_direction = 'OUT',
                    reference_object1 = starting_location.id.get(),
                    reference_object2 = ending_location.id.get()
                ))
            
        return references

    def get_attributes_from_topic(self, topic, attributes_template: list[MindmapAttribute]=[]) -> list[MindmapAttribute]:
        attributes = []
        return attributes

    def get_guid_from_topic(self, topic) -> str:
        return topic.id.get()
        
    def add_subtopic_to_topic(self, topic, topic_text):
        topic_instance = topic.get()
        return topic_instance.subtopics.end.make(new=k.topic, with_properties={k.name: topic_text})

    def set_topic_from_mindmap_topic(self, topic, mindmap_topic, map_icons):
        id = topic.id.get()
        self.set_text_to_topic(topic, mindmap_topic.topic_text)
        refreshed_topic = self.get_topic_by_id(id)
        if mindmap_topic.topic_rtf != '':
            self.set_title_to_topic(refreshed_topic, mindmap_topic.topic_rtf)
            refreshed_topic = self.get_topic_by_id(id)

        if mindmap_topic.topic_guid:
            mindmap_topic.topic_originalguid = mindmap_topic.topic_guid
        mindmap_topic.topic_guid = id

        return refreshed_topic

    def create_map_icons(self, map_icons):
        pass

    def add_relationship(self, guid1, guid2, label = ''):
        topic1 = self.get_topic_by_id(guid1)
        topic2 = self.get_topic_by_id(guid2)
        topic1.make(new=k.relationship, with_properties={k.starting_location: topic1, k.ending_location: topic2})

    def set_text_to_topic(self, topic, topic_text):
        topic.name.set(topic_text)

    def set_title_to_topic(self, topic, topic_rtf):
        topic.title.set(topic_rtf)

    def add_document(self, max_topic_level):
        cnt_subtopics = len(self.mindmanager.documents[1].central_topic.subtopics.get())
        if self.charttype == "orgchart":
            template_alias = self.orgchart_template
        if self.charttype == "radial":
            template_alias = self.radial_template
        if self.charttype == "auto":
            if max_topic_level > 2 and cnt_subtopics > 4:
                template_alias = self.orgchart_template
            else:
                template_alias = self.radial_template
        self.mindmanager.open(template_alias)

    def finalize(self, max_topic_level):
        self.mindmanager.documents[1].balance_map()
        self.mindmanager.activate()
        if self.MACOS_MERGE_ALL_WINDOWS:
            self.merge_windows()

        self.mindmanager = None
        del self.mindmanager
