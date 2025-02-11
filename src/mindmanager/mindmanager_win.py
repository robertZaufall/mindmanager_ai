import os
import sys
import re
import win32com.client
import winreg
import tempfile
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mindmap.mindmap_helper import MindmapLink, MindmapImage, MindmapNotes, MindmapIcon, MindmapTag, MindmapReference

RTF_WORKAROUND = False

class Mindmanager:

    def get_mindmanager_version():
        versions = ["26", "25", "24", "23"]
        for version in versions:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"Software\\Mindjet\\MindManager\\{version}\\AddIns")
                winreg.CloseKey(key)
                return version
            except FileNotFoundError:
                continue
        return None

    mindmanager_version = get_mindmanager_version()
    if mindmanager_version:
        WINDOWS_LIBRARY_FOLDER = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Mindjet", "MindManager", mindmanager_version, "Library", "ENU")
    else:
        raise Exception("No MindManager version registry keys found.")

    def __init__(self, charttype):
        self.mindmanager = win32com.client.Dispatch("Mindmanager.Application")
        self.mindmanager.Options.BalanceNewMainTopics = True
        self.charttype = charttype
        self.library_folder = self.WINDOWS_LIBRARY_FOLDER
        self.document = self.mindmanager.ActiveDocument
    
    def set_document_background_image(self, path):
        try:
            background = self.document.Background
            if background.HasImage:
                background.RemoveImage()
            background.InsertImage(path)
            background.TileOption = 1  # center
            background.Transparency = 88
        except Exception as e:
            print(f"Error setting document background image: {e}")

    def document_exists(self):
        try:
            return True if self.document else False
        except Exception as e:
            print(f"Error checking document existence: {e}")
            return False

    def get_central_topic(self):
        try:
            return self.document.CentralTopic
        except Exception as e:
            raise Exception(f"Error getting central topic: {e}")
    
    def get_topic_by_id(self, id):
        try:
            return self.document.FindByGuid(id)
        except Exception as e:
            print(f"Error in get_topic_by_id: {e}")
            return None

    def get_selection(self):
        try:
            return self.document.Selection
        except Exception as e:
            print(f"Error in get_selection: {e}")
            return None

    def get_level_from_topic(self, topic):
        try:
            return topic.Level
        except Exception as e:
            print(f"Error in get_level_from_topic: {e}")
            return None

    def get_text_from_topic(self, topic):
        try:
            return topic.Text.replace('"', '`').replace("'", "`").replace("\r", "").replace("\n", "")
        except Exception as e:
            print(f"Error in get_text_from_topic: {e}")
            return ""

    def get_title_from_topic(self, topic):
        try:
            title = topic.Title
            if RTF_WORKAROUND:
                return str(title.Text) + ''
            else:
                return title.TextRtf if title.TextRtf != '' else ''
        except Exception as e:
            print(f"Error in get_title_from_topic: {e}")
            return ""

    def get_subtopics_from_topic(self, topic):
        try:
            return topic.AllSubTopics
        except Exception as e:
            print(f"Error in get_subtopics_from_topic: {e}")
            return None
    
    def get_links_from_topic(self, topic) -> list[MindmapLink]:
        hyperlinks = []
        try:
            if topic.HasHyperlink:
                for hyperlink in topic.Hyperlinks:
                    hyperlinks.append(MindmapLink(
                        link_text=hyperlink.Title,
                        link_url=hyperlink.Address,
                        link_guid=hyperlink.TopicLabelGuid
                    ))
        except Exception as e:
            print(f"Error in get_links_from_topic: {e}")
        return hyperlinks

    def get_image_from_topic(self, topic) -> MindmapImage:
        try:
            if topic.HasImage:
                image = topic.Image
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    temp_filename = tmp.name
                image.Save(temp_filename, 3)  # 3=PNG
                return MindmapImage(image_text=temp_filename)
        except Exception as e:
            print(f"Error in get_image_from_topic: {e}")
        return None

    def get_icons_from_topic(self, topic) -> list[MindmapIcon]:
        icons = []
        try:
            user_icons = topic.UserIcons
            if user_icons.Count > 0:
                for icon in user_icons:
                    if icon.Type == 1 and icon.IsValid == True:  # Stock Icon
                        icons.append(MindmapIcon(
                            icon_text=icon.Name,
                            icon_index=icon.StockIcon
                        ))
                    elif icon.Type == 2 and icon.IsValid == True:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                            temp_filename = tmp.name
                        icon.Save(temp_filename, 3)  # 3=PNG
                        icons.append(MindmapIcon(
                            icon_text=icon.Name,
                            icon_is_stock_icon=False,
                            icon_signature=icon.CustomIconSignature,
                            icon_path=temp_filename
                        ))
        except Exception as e:
            print(f"Error in get_icons_from_topic: {e}")
        return icons

    def get_notes_from_topic(self, topic) -> MindmapNotes:
        try:
            notes = topic.Notes
            topic_notes = None
            if notes:
                if notes.IsValid == True and not notes.IsEmpty: 
                    if notes.TextRTF != "":
                        topic_notes = MindmapNotes(note_rtf=notes.TextRTF)
                    if notes.TextXHTML != "":
                        topic_notes = MindmapNotes(note_xhtml=notes.TextXHTML)
                    if notes.Text != "":
                        topic_notes = MindmapNotes(note_text=notes.Text)
            return topic_notes
        except Exception as e:
            print(f"Error in get_notes_from_topic: {e}")
            return None

    def get_tags_from_topic(self, topic) -> list[MindmapTag]:
        tags = []
        try:
            text_labels = topic.TextLabels
            if text_labels.Count > 0 and text_labels.IsValid == True:
                for text_label in text_labels:
                    if text_label.IsValid == True and text_label.GroupId == "":
                        tags.append(MindmapTag(tag_text=text_label.Name))
        except Exception as e:
            print(f"Error in get_tags_from_topic: {e}")
        return tags

    def get_references_from_topic(self, topic) -> list[MindmapReference]:
        references = []
        try:
            relationships = topic.AllRelationships
            if relationships.Count > 0 and relationships.IsValid == True:
                for relation in relationships:
                    if relation.IsValid == True:
                        connected_topic_guid_1 = relation.ConnectedObject1
                        connected_topic_guid_2 = relation.ConnectedObject2
                        reference_direction = 'OUT' if connected_topic_guid_1 == topic else 'IN'
                        references.append(MindmapReference(
                            reference_topic_guid_1=str(connected_topic_guid_1.Guid),
                            reference_topic_guid_2=str(connected_topic_guid_2.Guid),
                            reference_direction=reference_direction,
                            reference_label=''
                        ))
        except Exception as e:
            print(f"Error in get_references_from_topic: {e}")
        return references
    
    def get_guid_from_topic(self, topic) -> str:
        try:
            return topic.Guid
        except Exception as e:
            print(f"Error in get_guid_from_topic: {e}")
            return ""
        
    def add_subtopic_to_topic(self, topic, topic_text):
        try:
            return topic.AddSubtopic(topic_text)
        except Exception as e:
            print(f"Error in add_subtopic_to_topic: {e}")
            return None

    def get_parent_from_topic(self, topic):
        try:
            return topic.ParentTopic
        except Exception as e:
            print(f"Error in get_parent_from_topic: {e}")
            return None

    def set_text_to_topic(self, topic, topic_text):
        try:
            topic.Text = topic_text
        except Exception as e:
            print(f"Error in set_text_to_topic: {e}")

    def set_title_to_topic(self, topic, topic_rtf):
        try:
            if topic_rtf != "":
                if RTF_WORKAROUND:
                    topic.Title.Text = topic_rtf
                else:
                    topic.Title.TextRtf = topic_rtf
        except Exception as e:
            print(f"Error in set_title_to_topic: {e}")

    def add_tag_to_topic(self, tag_text, topic=None, topic_guid=None):
        try:
            if topic_guid:
                topic = self.get_topic_by_id(topic_guid)
            if topic:
                topic.TextLabels.AddTextLabelFromGroup(tag_text, '', True)
        except Exception as e:
            print(f"Error in add_tag_to_topic: {e}")

    def set_topic_from_mindmap_topic(self, topic, mindmap_topic, map_icons):
        self.set_text_to_topic(topic, mindmap_topic.topic_text)
        self.set_title_to_topic(topic, mindmap_topic.topic_rtf)
        self.add_tags_to_topic(topic, mindmap_topic.topic_tags)
        self.set_notes_to_topic(topic, mindmap_topic.topic_notes)
        self.add_icons_to_topic(topic, mindmap_topic.topic_icons, map_icons)
        self.add_image_to_topic(topic, mindmap_topic.topic_image)
        self.add_links_to_topic(topic, mindmap_topic.topic_links)
        return topic, topic.Guid
    
    def add_links_to_topic(self, topic, mindmap_topic_links):
        try:
            if mindmap_topic_links:
                for topic_link in mindmap_topic_links:
                    if topic_link.link_guid == "" and topic_link.link_url != "":
                        link = topic.Hyperlinks.AddHyperlink(topic_link.link_url)
                        link.Title = topic_link.link_text
        except Exception as e:
            print(f"Error in add_links_to_topic: {e}")

    def add_image_to_topic(self, topic, mindmap_topic_image):
        try:
            if mindmap_topic_image:
                topic.CreateImage(mindmap_topic_image.image_text)
        except Exception as e:
            print(f"Error in add_image_to_topic: {e}")

    def add_icons_to_topic(self, topic, mindmap_topic_icons, map_icons):
        try:
            if len(mindmap_topic_icons) > 0:
                for topic_icon in mindmap_topic_icons:
                    if topic_icon.icon_is_stock_icon:
                        topic.UserIcons.AddStockIcon(topic_icon.icon_index)
                    else:
                        if len(map_icons) > 0 and topic_icon.icon_signature != "":
                            topic.UserIcons.AddCustomIconFromMap(topic_icon.icon_signature)
                        else:
                            if os.path.exists(topic_icon.icon_path):
                                topic.UserIcons.AddCustomIcon(topic_icon.icon_path)
        except Exception as e:
            print(f"Error in add_icons_to_topic: {e}")

    def set_notes_to_topic(self, topic, mindmap_topic_notes):
        try:
            if mindmap_topic_notes:
                if mindmap_topic_notes.note_text:
                    topic.Notes.Text = mindmap_topic_notes.note_text
                else:
                    if mindmap_topic_notes.note_xhtml:
                        try:
                            topic.Notes.TextXHTML = mindmap_topic_notes.note_xhtml
                        except Exception as e:
                            print(f"Error setting TextXHTML: {e}")
                            print(f"Topic: `{topic.Text}`")
                    else:
                        if mindmap_topic_notes.note_rtf:
                            topic.Notes.TextRTF = mindmap_topic_notes.note_rtf
        except Exception as e:
            print(f"Error in set_notes_to_topic: {e}")


    def add_tags_to_topic(self, topic, mindmap_topic_tags):
        try:
            if len(mindmap_topic_tags) > 0:
                for topic_tag in mindmap_topic_tags:
                    topic.TextLabels.AddTextLabelFromGroup(topic_tag.tag_text, '', True)
        except Exception as e:
            print(f"Error in add_tags_to_topic: {e}")

    def create_map_icons(self, map_icons):
        try:
            if len(map_icons) > 0:
                icon_groups = set(map_icon.icon_group for map_icon in map_icons if map_icon.icon_group)
                for icon_group in icon_groups:
                    group = self.document.MapMarkerGroups.AddIconMarkerGroup(icon_group)
                    for map_icon in map_icons:
                        if map_icon.icon_group == icon_group:
                            label = map_icon.icon_text
                            marker = group.AddCustomIconMarker(label, map_icon.icon_path)
                            map_icon.icon_signature = marker.Icon.CustomIconSignature
        except Exception as e:
            print(f"Error in create_map_icons: {e}")

    def create_tags(self, tags: list['str'], DUPLICATED_TAG: str):
        try:
            if len(tags) > 0:
                map_marker_group = self.document.MapMarkerGroups.GetMandatoryMarkerGroup(10)
                for tag in tags:
                    map_marker_group.AddTextLabelMarker(tag)
                if DUPLICATED_TAG != '' and DUPLICATED_TAG not in tags:
                    map_marker_group.AddTextLabelMarker(DUPLICATED_TAG)
        except Exception as e:
            print(f"Error in create_tags: {e}")

    def add_relationship(self, guid1, guid2, label=''):
        try:
            object1 = self.get_topic_by_id(guid1)
            object2 = self.get_topic_by_id(guid2)
            if object1 and object2:
                if object1.ParentTopic == object2 or object2.ParentTopic == object1:
                    return
                object1.AllRelationships.AddToTopic(object2, label)
        except Exception as e:
            print(f"Error in add_relationship: {e}")

    def add_topic_link(self, guid1, guid2, label=''):
        try:
            object1 = self.get_topic_by_id(guid1)
            object2 = self.get_topic_by_id(guid2)
            if object1 and object2:
                hyperlinks = object1.Hyperlinks
                link = hyperlinks.AddHyperlinkToTopicByGuid(guid2)
                link.Title = label if label != "" else object2.Title.Text
        except Exception as e:
            print(f"Error in add_topic_link: {e}")

    def add_document(self, max_topic_level):
        try:
            style = self.document.StyleXml
            new_document = self.mindmanager.Documents.Add()
            new_document.StyleXml = style
            self.document = new_document
        except Exception as e:
            print(f"Error in add_document: {e}")

    def finalize(self, max_topic_level):
        try:
            centralTopic = self.document.CentralTopic
            layout = centralTopic.SubTopicsLayout
            growthDirection = layout.CentralTopicGrowthDirection
            cnt_subtopics = len(centralTopic.AllSubTopics)
                               
            # collapse/uncollapse outer topics
            if max_topic_level > 3:
                for topic in self.document.Range(2, True):  # 2 = all topics
                    if topic.Level > 2:
                        topic.Collapsed = True
                    else:
                        if topic.Level != 0:
                            topic.Collapsed = False
            else:
                for topic in self.document.Range(2, True):  # 2 = all topics
                    if topic.Level > 3:
                        topic.Collapsed = True
                    else:
                        if topic.Level != 0:
                            topic.Collapsed = False
                            
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

            self.document.Zoom(1)
            self.mindmanager.Visible = True
        except Exception as e:
            print(f"Error in finalize: {e}")