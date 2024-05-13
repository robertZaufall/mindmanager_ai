from appscript import *

class Mindmanager:

    def __init__(self, charttype):
        self.mindmanager = app('MindManager')
        self.charttype = charttype

    def document_exists(self):
        return self.mindmanager.documents[1].exists()

    def get_central_topic(self):
        return self.mindmanager.documents[1].central_topic.get()
    
    def get_selection(self):
        return self.mindmanager.documents[1].selection.get()
    
    def get_level_from_topic(self, topic):
        return topic.level.get()
    
    def get_title_from_topic(self, topic):
        return topic.title.get()

    def get_text_from_topic(self, topic):
        return topic.text.get()

    def get_subtopics_from_topic(self, topic):
        return topic.subtopics.get()

    def add_subtopic_to_topic(self, topic, topic_text):
        topic_instance = topic.get()
        return topic_instance.subtopics.end.make(new=k.topic, with_properties={k.name: topic_text})

    def set_title_to_topic(self, topic, topic_text):
        topic_instance = topic.get()
        topic_instance.title.set(topic_text)

    def add_document(self):
        if self.charttype == "orgchart":
            template_alias = mactypes.Alias('./macos/Org-Chart Map.mmat')
        if self.charttype == "radial":
            template_alias = mactypes.Alias('./macos/Radial Map.mmat')
        self.mindmanager.open(template_alias)
        # self.mindmanager.documents.end.make(new=k.document)

    def finalize(self, max_topic_level):
        self.mindmanager.documents[1].balance_map()
        self.mindmanager.activate()
