import os
import sys
from appscript import *
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mindmap.mindmap_helper import MindmapLink, MindmapImage, MindmapNotes, MindmapIcon, MindmapTag, MindmapReference, MindmapTopic

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
        try:
            return self.mindmanager.documents[1].exists()
        except Exception as e:
            print(f"Error checking document existence: {e}")
            return False

    def get_central_topic(self):
        try:
            topic = self.mindmanager.documents[1].central_topic.get()
            #callouts = topic.callouts.get()
            #relationships = topic.relationships.get()
            #subtopics = topic.subtopics.get()
            #shape = topic.shape.get()
            #attributes = topic.attributes.get()
            #props = topic.properties.get()
            #task = topic.task.get()
            #task_properties = task.properties.get()
            return topic
        except Exception as e:
            print(f"Error getting central topic: {e}")
            return None
    
    def get_topic_by_id(self, id):
        try:
            found_topics = self.mindmanager.documents[1].topics[its.id == id]
            if found_topics.count() == 0:
                return None
            return found_topics[0].get()
        except Exception as e:
            print(f"Error getting topic by id: {e}")
            return None
    
    def get_selection(self):
        try:
            return self.mindmanager.documents[1].selection.get()
        except Exception as e:
            print(f"Error getting selection: {e}")
            return None
    
    def get_level_from_topic(self, topic):
        try:
            return topic.level.get()
        except Exception as e:
            print(f"Error getting level from topic: {e}")
            return None
    
    def get_text_from_topic(self, topic):
        try:
            text = topic.name.get()
            return text.replace('"', '`').replace("'", "`").replace("\r", "").replace("\n", "")
        except Exception as e:
            print(f"Error getting text from topic: {e}")
            return ""
    
    def get_title_from_topic(self, topic):
        try:
            title = topic.title.get() 
            return title
        except Exception as e:
            print(f"Error getting title from topic: {e}")
            return ""
    
    def get_subtopics_from_topic(self, topic):
        try:
            return topic.subtopics.get()
        except Exception as e:
            print(f"Error getting subtopics from topic: {e}")
            return []

    def get_links_from_topic(self, topic) -> list['MindmapLink']:
        return None
        # this results in a severe runtime error of MindManager
        link = topic.hyperlink_URL.get()
        # this has no effect
        label = topic.label.get()
        return MindmapLink(link=link, label=label) if label != '' else None

    def get_image_from_topic(self, topic) -> MindmapImage:
        return None

    def get_icons_from_topic(self, topic) -> list[MindmapIcon]:
        return []

    def get_notes_from_topic(self, topic) -> MindmapNotes:
        try:
            return topic.notes.get()
        except Exception as e:
            print(f"Error getting notes from topic: {e}")
            return None

    def get_tags_from_topic(self, topic) -> list[MindmapTag]:
        return []

    def get_references_from_topic(self, topic) -> list[MindmapReference]:
        references = []
        try:
            relationships = topic.relationships.get()
            for relationship in relationships:
                relationship_instance = relationship.get()
                starting_location = relationship_instance.starting_location.get()
                ending_location = relationship_instance.ending_location.get()
                if starting_location == topic:
                    references.append(MindmapReference(
                        reference_direction='OUT',
                        reference_topic_guid_1=starting_location.id.get(),
                        reference_topic_guid_2=ending_location.id.get()
                    ))
        except Exception as e:
            print(f"Error in get_references_from_topic: {e}")
        return references

    def get_guid_from_topic(self, topic) -> str:
        try:
            return topic.id.get()
        except Exception as e:
            print(f"Error in get_guid_from_topic: {e}")
            return ""
        
    def add_subtopic_to_topic(self, topic, topic_text):
        try:
            topic_instance = topic.get()
            return topic_instance.subtopics.end.make(new=k.topic, with_properties={k.name: topic_text})
        except Exception as e:
            print(f"Error in add_subtopic_to_topic: {e}")
            return None

    def get_parent_from_topic(self, topic):
        try:
            return topic.parent.get()
        except Exception as e:
            print(f"Error in get_parent_from_topic: {e}")
            return None

    def set_text_to_topic(self, topic, topic_text):
        try:
            topic.name.set(topic_text)
        except Exception as e:
            print(f"Error in set_text_to_topic: {e}")

    def set_title_to_topic(self, topic, topic_rtf):
        try:
            topic.title.set(topic_rtf)
        except Exception as e:
            print(f"Error in set_title_to_topic: {e}")

    def add_tag_to_topic(self, topic, tag_text):
        pass

    def set_topic_from_mindmap_topic(self, topic, mindmap_topic, map_icons):
        try:
            topic_id = topic.id.get()
            self.set_text_to_topic(topic, mindmap_topic.topic_text)
            refreshed_topic = self.get_topic_by_id(topic_id)
            if mindmap_topic.topic_rtf != '':
                self.set_title_to_topic(refreshed_topic, mindmap_topic.topic_rtf)
                refreshed_topic = self.get_topic_by_id(topic_id)
            if mindmap_topic.topic_notes:
                refreshed_topic.notes.set(mindmap_topic.topic_notes)
                refreshed_topic = self.get_topic_by_id(topic_id)
            return refreshed_topic, topic_id
        except Exception as e:
            print(f"Error in set_topic_from_mindmap_topic: {e}")
            return None, None

    def create_map_icons(self, map_icons):
        pass

    def create_tags(self, tags: list['str'], DUPLICATED_TAG: str):
        pass

    def add_relationship(self, guid1, guid2, label = ''):
        try:
            topic1 = self.get_topic_by_id(guid1)
            topic2 = self.get_topic_by_id(guid2)
            if topic1 is None or topic2 is None:
                print("Error in add_relationship: One or both topics not found.")
                return
            topic1.make(new=k.relationship, with_properties={k.starting_location: topic1, k.ending_location: topic2})
        except Exception as e:
            print(f"Error in add_relationship: {e}")

    def add_topic_link(self, guid1, guid2, label=''):
        pass

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
