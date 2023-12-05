import win32com.client

class Mindmanager:

    def __init__(self):
        self.mindmanager = win32com.client.Dispatch("Mindmanager.Application")
        self.mindmanager.Options.BalanceNewMainTopics = True

    def document_exists(self):
        return True if self.mindmanager.ActiveDocument else False

    def get_central_topic(self):
        return self.mindmanager.ActiveDocument.CentralTopic
    
    def get_selection(self):
        return self.mindmanager.ActiveDocument.Selection
    
    def get_level_from_topic(self, topic):
        return topic.Level
    
    def get_title_from_topic(self, topic):
        return topic.Text

    def get_text_from_topic(self, topic):
        return topic.Text

    def get_subtopics_from_topic(self, topic):
        return topic.AllSubTopics

    def add_subtopic_to_topic(self, topic, topic_text):
        return topic.AddSubtopic(topic_text)

    def set_title_to_topic(self, topic, topic_text):
        topic.Text = topic_text

    def add_document(self):
        self.mindmanager.Documents.Add()

    def finalize(self):
        self.mindmanager.ActiveDocument.Zoom(1)
        self.mindmanager.Visible = True
