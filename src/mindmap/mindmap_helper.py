import sys
import os

DUPLICATED_TAG = 'Duplicated'
DUPLICATE_LABEL = 'DUPLICATE'

class MindmapLink:
    def __init__(self, link_text: str = '', link_url: str = '', link_guid: str = ''):
        self.link_text = link_text
        self.link_url = link_url
        self.link_guid = link_guid

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
                 icon_path: str = '',
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
                 topic_links: list['MindmapLink'] = None,
                 topic_image: 'MindmapImage' = None,
                 topic_icons: list['MindmapIcon'] = None,
                 topic_notes: 'MindmapNotes' = None,
                 topic_tags: list['MindmapTag'] = None,
                 topic_references: list['MindmapReference'] = None,
                 topic_attributes: list['MindmapAttribute'] = None):
        self.topic_guid = topic_guid
        self.topic_originalguid = topic_originalguid
        self.topic_text = topic_text.replace('"', '`').replace("'", "`").replace("\r", "").replace("\n", "")
        self.topic_rtf = topic_rtf
        self.topic_level = topic_level
        self.topic_selected = topic_selected
        self.topic_parent = topic_parent
        self.topic_subtopics = topic_subtopics if topic_subtopics is not None else []
        self.topic_links = topic_links if topic_links is not None else []
        self.topic_image = topic_image
        self.topic_icons = topic_icons if topic_icons is not None else []
        self.topic_notes = topic_notes
        self.topic_tags = topic_tags if topic_tags is not None else []
        self.topic_references = topic_references if topic_references is not None else []
        self.topic_attributes = topic_attributes if topic_attributes is not None else [MindmapAttribute(attribute_name='id')]

class MindmapDocument:

    def __init__(self, charttype: str = 'auto', turbo_mode: bool = False, inline_editing_mode: bool = False, mermaid_mode: bool = True):
        self.charttype: str = charttype
        self.turbo_mode: bool = turbo_mode
        self.inline_editing_mode: bool = inline_editing_mode
        self.mermaid_mode: bool = mermaid_mode
        self.mindmap: 'MindmapTopic' = None
        self.central_topic_selected: bool = False
        self.selected_topic_texts: list[str] = []
        self.selected_topic_levels: list[int] = []
        self.selected_topic_ids: list[str] = []
        self.max_topic_level: int = 0

        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        if sys.platform.startswith('win'):
            import mindmanager.mindmanager_win as mindmanager
            platform = "win"
        elif sys.platform.startswith('darwin'):
            import mindmanager.mindmanager_mac as mindmanager
            platform = "darwin"

        self.mindm = mindmanager.Mindmanager(charttype)

    def get_mindmap(self, topic=None, attributes_template: list['MindmapAttribute'] = None):
        if not self.mindm.document_exists():
            print("No document found. Please open MindManager with a document.")    
            return False

        if attributes_template is None:
            attributes_template = [MindmapAttribute(attribute_name='id')]
        
        if topic is None:
            topic = self.mindm.get_central_topic()
        
        mindmap = self.get_mindmap_topic_from_topic(topic, attributes_template=attributes_template)

        selection = self.get_selection()
        selected_topic_texts, selected_topic_levels, selected_topic_ids, central_topic_selected = self.get_topic_texts_from_selection(selection)
        self.central_topic_selected = central_topic_selected
        self.selected_topic_texts = selected_topic_texts
        self.selected_topic_levels = selected_topic_levels
        self.selected_topic_ids = selected_topic_ids
        self.max_topic_level = self.get_max_topic_level(mindmap)
        self.mindmap = mindmap
        return True

    def get_max_topic_level(self, mindmap_topic, max_topic_level = 0):
        for mindmap_subtopic in mindmap_topic.topic_subtopics:
            if mindmap_subtopic.topic_level > max_topic_level:
                max_topic_level = mindmap_subtopic.topic_level
            max_topic_level = self.get_max_topic_level(mindmap_subtopic, max_topic_level)
        return max_topic_level

    def get_parent_topic(self, topic):
        topic_level = self.mindm.get_level_from_topic(topic)
        if topic_level == 0:
            return None
        parent_topic = self.mindm.get_parent_from_topic(topic)
        parent_mindmap_topic = MindmapTopic(
            topic_guid=self.mindm.get_guid_from_topic(parent_topic),
            topic_text=self.mindm.get_text_from_topic(parent_topic), 
            topic_level=self.mindm.get_level_from_topic(parent_topic),
            topic_parent=self.get_parent_topic(parent_topic),
        )
        return parent_mindmap_topic

    def get_selection(self):
        selection = self.mindm.get_selection()
        mindmap_topics = []
        for topic in selection:
            topic_level = self.mindm.get_level_from_topic(topic)
            mindmap_topic = MindmapTopic(
                topic_guid=self.mindm.get_guid_from_topic(topic),
                topic_text=self.mindm.get_text_from_topic(topic), 
                topic_level=topic_level,
                topic_parent=self.get_parent_topic(topic),
                topic_selected=True,
            )
            mindmap_topics.append(mindmap_topic)
        return mindmap_topics

    def get_mindmap_topic_from_topic(self, topic, parent_topic=None, attributes_template: list['MindmapAttribute'] = None):
        if attributes_template is None:
            attributes_template = []
        mindmap_topic = MindmapTopic(
            topic_guid=self.mindm.get_guid_from_topic(topic),
            topic_text=self.mindm.get_text_from_topic(topic),
            topic_rtf=self.mindm.get_title_from_topic(topic),
            topic_level=self.mindm.get_level_from_topic(topic),
            topic_links=self.mindm.get_links_from_topic(topic),
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
                references.append(MindmapReference(
                    reference_object1=reference.reference_object1,
                    reference_object2=reference.reference_object2,
                    reference_direction=reference.reference_direction,
                    reference_label=reference.reference_label
                ))
        for mindmap_subtopic in mindmap.topic_subtopics:
            self.get_relationships_from_mindmap(mindmap_subtopic, references)

    def get_topic_links_from_mindmap(self, mindmap, links):
        for link in mindmap.topic_links:
            if link.link_guid != '':
                links.append(MindmapReference(
                    reference_object1=mindmap.topic_guid, 
                    reference_object2=link.link_guid, 
                    reference_direction='OUT', 
                    reference_label=link.link_text
                ))
        for mindmap_subtopic in mindmap.topic_subtopics:
            self.get_topic_links_from_mindmap(mindmap_subtopic, links)

    def get_tags_from_mindmap(self, mindmap, tags):
        for tag in mindmap.topic_tags:
            if tag.tag_text != '' and tag.tag_text not in tags:
                tags.append(tag.tag_text)
        for mindmap_subtopic in mindmap.topic_subtopics:
            self.get_tags_from_mindmap(mindmap_subtopic, tags)

    def get_parents_from_mindmap(self, mindmap, parents):
        for subtopic in mindmap.topic_subtopics:
            if subtopic.topic_guid not in parents:
                parents[subtopic.topic_guid] = mindmap.topic_guid
                self.get_parents_from_mindmap(subtopic, parents)
            return

    def get_map_icons_and_fix_refs_from_mindmap(self, mindmap, map_icons: list['MindmapIcon']):
        for i, topic_icon_ref in enumerate(mindmap.topic_icons):
            if not topic_icon_ref.icon_is_stock_icon and topic_icon_ref.icon_group == 'Types':
                found = False
                for map_icon in map_icons:
                    if map_icon.icon_signature == topic_icon_ref.icon_signature:
                        found = True
                        new_icon = map_icon
                        break
                if not found:
                    new_icon = MindmapIcon(
                        icon_text=topic_icon_ref.icon_text, 
                        icon_index=topic_icon_ref.icon_index,
                        icon_is_stock_icon=topic_icon_ref.icon_is_stock_icon, 
                        icon_path=topic_icon_ref.icon_path,
                        icon_signature=topic_icon_ref.icon_signature,
                        icon_group = topic_icon_ref.icon_group)                
                    map_icons.append(new_icon)
                mindmap.topic_icons[i] = new_icon
        for mindmap_subtopic in mindmap.topic_subtopics:
            self.get_map_icons_and_fix_refs_from_mindmap(mindmap_subtopic, map_icons)

    def get_topic_texts_from_selection(self, mindmap_topics):
        topic_texts = []
        topic_levels = []
        topic_ids = []
        central_topic_selected = False
        for mindmap_topic in mindmap_topics:
            if mindmap_topic.topic_selected:
                if mindmap_topic.topic_level > 0:
                    topic_texts.append(mindmap_topic.topic_text)
                    topic_levels.append(mindmap_topic.topic_level)
                    topic_ids.append(mindmap_topic.topic_guid)
                else:
                    central_topic_selected = True
        return topic_texts, topic_levels, topic_ids, central_topic_selected
            
    def clone_mindmap_topic(self, mindmap_topic, subtopics: list['MindmapTopic'] = None, attributes: list['MindmapAttribute']=None, parent=None):
        cloned_subtopics = []
        if subtopics is not None:
            for subtopic in subtopics:
                cloned_subtopic = self.clone_mindmap_topic(subtopic)
                cloned_subtopics.append(cloned_subtopic)
        cloned_attributes = []
        if attributes is not None:
            for attribute in attributes:
                cloned_attribute = MindmapAttribute(
                    attribute_namespace=attribute.attribute_namespace,
                    attribute_name=attribute.attribute_name,
                    attribute_value=attribute.attribute_value
                )
                cloned_attributes.append(cloned_attribute)
        return MindmapTopic(
            topic_guid=mindmap_topic.topic_guid,
            topic_originalguid=mindmap_topic.topic_originalguid,
            topic_text=mindmap_topic.topic_text, 
            topic_rtf=mindmap_topic.topic_rtf,
            topic_level=mindmap_topic.topic_level,
            topic_parent=parent,
            topic_links=mindmap_topic.topic_links,
            topic_image=mindmap_topic.topic_image,
            topic_icons=mindmap_topic.topic_icons,
            topic_notes=mindmap_topic.topic_notes,
            topic_tags=mindmap_topic.topic_tags,
            topic_attributes=cloned_attributes,
            topic_subtopics=cloned_subtopics
        )

    def create_relationship_to_parent(self, mindmap_topic, done):
        parent = mindmap_topic.topic_parent
        parent_id = self.get_attribute_from_mindmap_topic(parent.topic_attributes, 'id')
        if parent_id:
            link_from = mindmap_topic.topic_guid
            if parent_id in done:
                link_to = done[parent_id]
                self.mindm.add_relationship(link_from, link_to)

    def update_done(self, topic_guid, mindmap_topic, level, done, done_global):
        if mindmap_topic.topic_guid == '':
            return
        if level <= 1:
            done = {}
        elif level >= 2: 
            done[mindmap_topic.topic_guid] = [topic_guid] if mindmap_topic.topic_guid not in done else done[mindmap_topic.topic_guid] + [topic_guid]
        if mindmap_topic.topic_guid in done_global:
            if self.guid_counts[mindmap_topic.topic_guid]['child'] < 11 and self.guid_counts[mindmap_topic.topic_guid]['parent'] >= 0:
                for i in range(len(done_global[mindmap_topic.topic_guid])):
                    link_from = topic_guid
                    link_to = done_global[mindmap_topic.topic_guid][i]
                    self.mindm.add_topic_link(link_from, link_to, DUPLICATE_LABEL)
                    self.mindm.add_topic_link(link_to, link_from, DUPLICATE_LABEL)
                if len(done_global[mindmap_topic.topic_guid]) == 1:
                    self.mindm.add_tag_to_topic(DUPLICATED_TAG, topic_guid = done_global[mindmap_topic.topic_guid][0])
            self.mindm.add_tag_to_topic(DUPLICATED_TAG, topic_guid = topic_guid)
            done_global[mindmap_topic.topic_guid] = done_global[mindmap_topic.topic_guid] + [topic_guid]
        else:
            done_global[mindmap_topic.topic_guid] = [topic_guid]

    def set_topic_from_mindmap_topic(self, topic, mindmap_topic, map_icons, done = {}, done_global = {}, level=0):
        if self.turbo_mode:
            topic_guid = self.mindm.get_guid_from_topic(topic)
            self.update_done(topic_guid, mindmap_topic, level, done, done_global)
            for mindmap_subtopic in mindmap_topic.topic_subtopics:
                subtopic = self.mindm.add_subtopic_to_topic(topic, mindmap_subtopic.topic_text)
                self.set_topic_from_mindmap_topic(subtopic, mindmap_subtopic, map_icons, done, done_global, level+1)
        else:
            topic, topic_guid = self.mindm.set_topic_from_mindmap_topic(topic, mindmap_topic, map_icons)
            self.update_done(topic_guid, mindmap_topic, level, done, done_global)

            if mindmap_topic.topic_subtopics and len(mindmap_topic.topic_subtopics) > 0:
                mindmap_topic.topic_subtopics.sort(key=lambda subtopic: subtopic.topic_text)
    
            for mindmap_subtopic in mindmap_topic.topic_subtopics:
                if mindmap_subtopic.topic_guid in done:
                    #create_relationship_to_parent(mindm, mindmap_subtopic, done)
                    this_guid_as_parent_exists = self.check_parent_exists(topic_guid, mindmap_subtopic.topic_guid)
                    if not this_guid_as_parent_exists:
                        cloned_subtopic = self.clone_mindmap_topic(mindmap_subtopic)
                        subtopic = self.mindm.add_subtopic_to_topic(topic, cloned_subtopic.topic_text)
                        self.set_topic_from_mindmap_topic(subtopic, cloned_subtopic, map_icons, done, done_global, level+1)
                    else:
                        pass
                else:
                    subtopic = self.mindm.add_subtopic_to_topic(topic, mindmap_subtopic.topic_text)
                    self.set_topic_from_mindmap_topic(subtopic, mindmap_subtopic, map_icons, done, done_global, level+1)
        return mindmap_topic

    def check_parent_exists(self, topic_guid, this_guid):
        check = False
        if topic_guid in self.parents:
            parent_guid = self.parents[topic_guid]
            if parent_guid == this_guid:
                check = True
            else:
                check = self.check_parent_exists(parent_guid, this_guid)
        return check

    def create_mindmap(self):
        self.parents = {}
        tags = []
        map_icons = []
        relationships = []
        links = []

        self.guid_counts = {}
        def count_parent_and_child_occurrences(topic):
            if topic.topic_guid:
                if topic.topic_guid not in self.guid_counts:
                    self.guid_counts[topic.topic_guid] = {'parent': 0, 'child': 0}
                for subtopic in topic.topic_subtopics:
                    if topic.topic_guid:
                        self.guid_counts[topic.topic_guid]['parent'] += 1
                    if subtopic.topic_guid:
                        if subtopic.topic_guid not in self.guid_counts:
                            self.guid_counts[subtopic.topic_guid] = {'parent': 0, 'child': 0}
                        self.guid_counts[subtopic.topic_guid]['child'] += 1
                    count_parent_and_child_occurrences(subtopic)
        count_parent_and_child_occurrences(self.mindmap)

        self.get_parents_from_mindmap(self.mindmap, self.parents)
        self.get_tags_from_mindmap(self.mindmap, tags)
        self.get_map_icons_and_fix_refs_from_mindmap(self.mindmap, map_icons)
        self.get_relationships_from_mindmap(self.mindmap, relationships)
        self.get_topic_links_from_mindmap(self.mindmap, links)

        self.mindm.add_document(0)
        self.mindm.create_map_icons(map_icons)
        self.mindm.create_tags(tags, DUPLICATED_TAG)
        self.mindm.set_text_to_topic(self.mindm.get_central_topic(), self.mindmap.topic_text)
        topic = self.mindm.get_central_topic()

        done_global = {}
        self.set_topic_from_mindmap_topic(topic=topic, mindmap_topic=self.mindmap, map_icons=map_icons, done={}, done_global=done_global)

        for reference in relationships:
            object1_guids = done_global[reference.reference_object1]
            object2_guids = done_global[reference.reference_object2]
            for object1_guid in object1_guids:
                for object2_guid in object2_guids:
                    self.mindm.add_relationship(object1_guid, object2_guid, reference.reference_label)

        for link in links:
            object1_guids = done_global[link.reference_object1]
            object2_guids = done_global[link.reference_object2]
            for object1_guid in object1_guids:
                for object2_guid in object2_guids:
                    self.mindm.add_topic_link(object1_guid, object2_guid, link.reference_label)

    def create_mindmap_and_finalize(self):
        self.create_mindmap()
        self.finalize()

    def finalize(self):
        if self.max_topic_level == 0:
            self.max_topic_level = self.get_max_topic_level(self.mindmap)
        self.mindm.finalize(self.max_topic_level)
    
    def set_background_image(self, image_path):
        self.mindm.set_document_background_image(image_path)
    
    def get_library_folder(self):
        return self.mindm.library_folder
    
    def get_grounding_information(self):
        central_topic_text = self.mindmap.topic_text
        subtopics = ""
        if len(self.selected_topic_texts) == 0: 
            top_most_topic = central_topic_text
        else:
            if self.central_topic_selected:
                top_most_topic = central_topic_text
                subtopics =  ",".join(self.selected_topic_texts)
            else:
                min_level = min(self.selected_topic_levels)
                max_level = max(self.selected_topic_levels)
                if (min_level == max_level):
                    top_most_topic = central_topic_text
                    subtopics =  ",".join(self.selected_topic_texts)
                else:
                    top_most_topic = ""
                    for i in range(len(self.selected_topic_levels)):
                        if self.selected_topic_levels[i] != max_level:
                            top_most_topic += self.selected_topic_texts[i] + "/"
                        else:
                            subtopics += self.selected_topic_texts[i] + ","

                    if top_most_topic.endswith("/"):
                        top_most_topic = top_most_topic[:-1]
                    if subtopics.endswith(","):
                        subtopics = subtopics[:-1]        
        return top_most_topic, subtopics