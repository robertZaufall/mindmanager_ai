import win32com.client
import config
import os
import mindmap_helper
import tempfile

class Mindmanager:

    def __init__(self, charttype):
        self.mindmanager = win32com.client.Dispatch("Mindmanager.Application")
        self.mindmanager.Options.BalanceNewMainTopics = True
        self.charttype = charttype
        self.library_folder = config.WINDOWS_LIBRARY_FOLDER
    
    def set_document_background_image(self, path):
        bg_object = self.mindmanager.ActiveDocument.Background
        if bg_object.HasImage:
            bg_object.RemoveImage
        bg_object.InsertImage(path)
        bg_object.TileOption = 1 # center
        bg_object.Transparency = 88

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
    
    def get_link_from_topic(self, topic) -> mindmap_helper.MindmapLink:
        if topic.HasHyperlink:
            hyperlink = topic.Hyperlink
            return mindmap_helper.MindmapLink(
                link_text = hyperlink.Title,
                link_url = hyperlink.Address
            )
        return None

    def get_image_from_topic(self, topic) -> mindmap_helper.MindmapImage:
        if topic.HasImage:
            image = topic.Image
            temp_filename = tempfile.mktemp(suffix=".png")
            image.Save(temp_filename, 3) # 3=PNG
            return mindmap_helper.MindmapImage(
                image_text = temp_filename
            )
        return None

    def get_icons_from_topic(self, topic) -> list[mindmap_helper.MindmapIcon]:
        icons = []
        user_icons = topic.UserIcons
        if user_icons.Count > 0:
            for icon in user_icons:
                if icon.Type == 1 and icon.IsValid == True: # Stock Icon
                    icons.append(mindmap_helper.MindmapIcon(
                        icon_text = icon.Name,
                        icon_index = icon.StockIcon
                    ))
        return icons

    def get_notes_from_topic(self, topic) -> mindmap_helper.MindmapNotes:
        topic_notes = topic.Notes
        if topic_notes:
            if topic_notes.IsPlainTextOnly == True and topic_notes.IsValid == True and not topic_notes.IsTextEmpty:
                return mindmap_helper.MindmapNotes(
                    note_text = topic_notes.Text
                )
        return None

    def get_tags_from_topic(self, topic) -> list[mindmap_helper.MindmapTag]:
        return []

    def get_references_from_topic(self, topic) -> list[mindmap_helper.MindmapReference]:
        return []
        
    def add_subtopic_to_topic(self, topic, topic_text):
        return topic.AddSubtopic(topic_text)

    def set_title_to_topic(self, topic, topic_text):
        topic.Text = topic_text

    def add_document(self, max_topic_level):
        style = self.mindmanager.ActiveDocument.StyleXml
        self.mindmanager.Documents.Add()
        self.mindmanager.ActiveDocument.StyleXml = style

    def finalize(self, max_topic_level):
        centralTopic = self.mindmanager.ActiveDocument.CentralTopic
        layout = centralTopic.SubTopicsLayout
        growthDirection = layout.CentralTopicGrowthDirection
        cnt_subtopics = len(centralTopic.AllSubTopics)
                           
        # collapse/uncollapse outer topics
        if max_topic_level > 3:
            for topic in self.mindmanager.ActiveDocument.Range(2, True): # 2 = all topics
                if topic.Level > 2:
                    topic.Collapsed = True
                else:
                    if topic.Level != 0: topic.Collapsed = False
        else:
            for topic in self.mindmanager.ActiveDocument.Range(2, True): # 2 = all topics
                if topic.Level > 3:
                    topic.Collapsed = True
                else:
                    if topic.Level != 0: topic.Collapsed = False
        # org chart            
        if self.charttype == "orgchart" or self.charttype == "auto":
            if max_topic_level > 2 and cnt_subtopics > 4:
                if growthDirection == 1:
                    layout.CentralTopicGrowthDirection = 5
        # radial map
        if self.charttype == "radial" or self.charttype == "auto":
            if max_topic_level > 2 and cnt_subtopics < 5:
                if growthDirection != 1:
                    layout.CentralTopicGrowthDirection = 1
            if max_topic_level < 3 and cnt_subtopics > 4:
                if growthDirection != 1:
                    layout.CentralTopicGrowthDirection = 1

        self.mindmanager.ActiveDocument.Zoom(1)
        self.mindmanager.Visible = True
