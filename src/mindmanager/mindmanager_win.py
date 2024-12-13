import os
import sys
import win32com.client
import tempfile
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mindmap.mindmap_helper import *


class Mindmanager:

    WINDOWS_LIBRARY_FOLDER = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Mindjet", "MindManager", "23", "Library", "ENU")

    def __init__(self, charttype):
        self.mindmanager = win32com.client.Dispatch("Mindmanager.Application")
        self.mindmanager.Options.BalanceNewMainTopics = True
        self.charttype = charttype
        self.library_folder = self.WINDOWS_LIBRARY_FOLDER
    
    def set_document_background_image(self, path):
        background = self.mindmanager.ActiveDocument.Background
        if background.HasImage:
            background.RemoveImage
        background.InsertImage(path)
        background.TileOption = 1 # center
        background.Transparency = 88

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
    
    def get_link_from_topic(self, topic) -> MindmapLink:
        if topic.HasHyperlink:
            hyperlink = topic.Hyperlink
            return MindmapLink(
                link_text = hyperlink.Title,
                link_url = hyperlink.Address
            )
        return None

    def get_image_from_topic(self, topic) -> MindmapImage:
        if topic.HasImage:
            image = topic.Image
            temp_filename = tempfile.mktemp(suffix=".png")
            image.Save(temp_filename, 3) # 3=PNG
            return MindmapImage(
                image_text = temp_filename
            )
        return None

    def get_icons_from_topic(self, topic) -> list[MindmapIcon]:
        icons = []
        user_icons = topic.UserIcons
        if user_icons.Count > 0:
            for icon in user_icons:
                if icon.Type == 1 and icon.IsValid == True: # Stock Icon
                    icons.append(MindmapIcon(
                        icon_text = icon.Name,
                        icon_index = icon.StockIcon
                    ))
                elif icon.Type == 2 and icon.IsValid == True:
                    temp_filename = tempfile.mktemp(suffix=".png")
                    icon.Save(temp_filename, 3) # 3=PNG
                    icons.append(MindmapIcon(
                        icon_text = icon.Name,
                        icon_is_stock_icon = False,
                        icon_signature = icon.CustomIconSignature,
                        icon_path = temp_filename
                    ))
        return icons

    def get_notes_from_topic(self, topic) -> MindmapNotes:
        topic_notes = topic.Notes
        if topic_notes:
            if topic_notes.IsValid == True and not topic_notes.IsEmpty: 
                if topic_notes.TextRTF != "":
                    return MindmapNotes(note_rtf = topic_notes.TextRTF)
                if topic_notes.TextXHTML != "":
                    return MindmapNotes(note_xhtml = topic_notes.TextXHTML)
                if topic_notes.Text != "":
                    return MindmapNotes(note_text = topic_notes.Text)
        return None

    def get_tags_from_topic(self, topic) -> list[MindmapTag]:
        tags = []
        text_labels = topic.TextLabels
        if text_labels.Count > 0 and text_labels.IsValid == True:
            for text_label in text_labels:
                if text_label.IsValid == True and text_label.GroupId == "":
                    tags.append(MindmapTag(
                        tag_text = text_label.Name
                    ))
        return tags

    def get_references_from_topic(self, topic) -> list[MindmapReference]:
        references = []
        relationships = topic.AllRelationships
        if relationships.Count > 0 and relationships.IsValid == True:
            for relation in relationships:
                if relation.IsValid == True:
                    connected_object1 = relation.ConnectedObject1
                    connected_object2 = relation.ConnectedObject2
                    reference_direction = 'OUT' if connected_object1 == topic else 'IN'
                    references.append(MindmapReference(
                        reference_object1 = str(connected_object1.Guid),
                        reference_object2 = str(connected_object2.Guid),
                        reference_direction = reference_direction,
                        reference_label = ''
                    ))
        return references
    
    def get_guid_from_topic(self, topic) -> str:
        return topic.Guid
        
    def add_subtopic_to_topic(self, topic, topic_text):
        return topic.AddSubtopic(topic_text)

    def set_topic_from_mindmap_topic(self, topic, mindmap_topic, map_icons):
        if topic.Text != mindmap_topic.topic_text:
            topic.Text = mindmap_topic.topic_text

        if len(mindmap_topic.topic_tags) > 0:
            for topic_tag in mindmap_topic.topic_tags:
                topic.TextLabels.AddTextLabel(topic_tag.tag_text, True) # toggleIfMapMarker
        
        if mindmap_topic.topic_notes:
            if mindmap_topic.topic_notes.note_text:
                topic.Notes.Text = mindmap_topic.topic_notes.note_text
            else:
                if mindmap_topic.topic_notes.note_xhtml:
                    topic.Notes.TextXHTML = mindmap_topic.topic_notes.note_xhtml
                else:
                    if mindmap_topic.topic_notes.note_rtf:
                        topic.Notes.TextRTF = mindmap_topic.topic_notes.note_rtf
        
        if len(mindmap_topic.topic_icons) > 0:
            for topic_icon in mindmap_topic.topic_icons:
                if topic_icon.icon_is_stock_icon:
                    topic.UserIcons.AddStockIcon(topic_icon.icon_index)
                else:
                    if len(map_icons) > 0 and topic_icon.icon_signature != "":
                        topic.UserIcons.AddCustomIconFromMap(topic_icon.icon_signature)
                    else:
                        if os.path.exists(topic_icon.icon_path):
                            topic.UserIcons.AddCustomIcon(topic_icon.icon_path)
        
        if mindmap_topic.topic_image:
            topic.CreateImage(mindmap_topic.topic_image.image_text)
        
        if mindmap_topic.topic_link:
            topic.CreateHyperlink(mindmap_topic.topic_link.link_url)
            for link in topic.Hyperlinks:
                link.Title = mindmap_topic.topic_link.link_text
                break
        
        if mindmap_topic.topic_guid:
            mindmap_topic.topic_originalguid = mindmap_topic.topic_guid
        mindmap_topic.topic_guid = topic.Guid

    def add_relationship(self, guid1, guid2, label):
        object1 = self.mindmanager.ActiveDocument.FindByGuid(guid1)
        object2 = self.mindmanager.ActiveDocument.FindByGuid(guid2)
        object1.AllRelationships.AddToTopic(object2, label)

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
