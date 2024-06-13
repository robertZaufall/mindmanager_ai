#!/usr/bin/env python3
import config
import prompts
import llm
import mermaid
import sys

if sys.platform.startswith('win'):
    import mindmanager_win as mindmanager
    platform = "win"
elif sys.platform.startswith('darwin'):
    import mindmanager_mac as mindmanager
    platform = "darwin"

def recurse_topics(mindm, mermaid_diagram, this_topic, level):
    this_topic_text = mindm.get_title_from_topic(this_topic)
    
    if level == 0:
        top_level = mermaid.get_mermaid_line(0, this_topic_text)
        mermaid_diagram = recurse_topics(mindm, top_level, this_topic, 1)
        return mermaid_diagram

    if level > 1:
        mermaid_diagram += mermaid.get_mermaid_line(level, this_topic_text)

    for child_topic in mindm.get_subtopics_from_topic(this_topic):
        mermaid_diagram = recurse_topics(mindm, mermaid_diagram, child_topic, level + 1)
    
    return mermaid_diagram

def create_sub_topics(mindm, mermaid_topics, index, parent_topic):
    i = index
    parent_topic_level = mindm.get_level_from_topic(parent_topic)

    last_topic = None
    while i < len(mermaid_topics):
        topic_level = mermaid_topics[i].topic_level
        topic_text = mermaid_topics[i].topic_text

        if topic_level <= parent_topic_level: return i

        if topic_level == parent_topic_level + 1:
            new_topic = mindm.add_subtopic_to_topic(parent_topic, topic_text)
            last_topic = new_topic

        if topic_level > parent_topic_level + 1:
            i = create_sub_topics(mindm, mermaid_topics, i, last_topic) - 1

        i += 1
    return i

def get_mermaid_topics(mindm, mermaid_diagram):
    mermaid_topics = mermaid.parse_mermaid(mermaid_diagram, config.LINE_SEPARATOR, config.INDENT_SIZE)
    max_topic_level = max(topic.topic_level for topic in mermaid_topics)
    return (mermaid_topics, max_topic_level)

def create_new_map_from_mermaid(mindm, mermaid_diagram):
    (mermaid_topics, max_topic_level) = get_mermaid_topics(mindm, mermaid_diagram)
    mindm.add_document(max_topic_level)
    parent_topic = mindm.get_central_topic()
    mindm.set_title_to_topic(parent_topic, mermaid_topics[0].topic_text)
    create_sub_topics(mindm, mermaid_topics, 1, mindm.get_central_topic())
    return max_topic_level


def main(param, charttype):
    mindm = mindmanager.Mindmanager(charttype)

    if not mindm.document_exists():
        print("No document found.")    
        return

    central_topic = mindm.get_central_topic()
    mermaid_diagram = recurse_topics(mindm, "", central_topic, 0)

    if param != "finalize":
        prompts_list = prompts.prompts_list_from_param(param)

        if mindm.document_exists():
            topic_texts = ""

            if len(prompts_list) == 1:
                selection = mindm.get_selection()
                if len(selection) > 0:
                    for this_topic in selection:
                        if mindm.get_level_from_topic(this_topic) > 0:
                            topic_texts += mindm.get_title_from_topic(this_topic) + ","
                        
                    if len(topic_texts) > 0: topic_texts = topic_texts[:-1]

            if param == "image":
                if len(topic_texts) == 0: topic_texts = mindm.get_title_from_topic(central_topic)
                image_result = llm.call_llm_image(prompts.prompt_image(topic_texts))

            else:
                new_mermaid_diagram = llm.call_llm_sequence(prompts_list, mermaid_diagram, topic_texts)

                if new_mermaid_diagram != "":
                    max_topic_level = create_new_map_from_mermaid(mindm, new_mermaid_diagram)
                    mindm.finalize(max_topic_level)
    
    elif param == "finalize":
        if platform == "win":
            max_topic_level = get_mermaid_topics(mindm, mermaid_diagram)[1]
        else:
            max_topic_level = create_new_map_from_mermaid(mindm, mermaid_diagram)
        mindm.finalize(max_topic_level)

    print("Done.")

if __name__ == "__main__":
    
    # refine, refine_dev
    # complexity_1, complexity_2, complexity_3
    # examples, cluster, exp, capex_opex
    # prc_org, prj_prc_org, exp_prj_prc_org, prj_org
    # finalize (no llm call - just existing (win) or new map (macos) with defined charttype / formattings)
    # image (experimental)
    param = "refine" 

    # radial, orgchart, auto (-> on macos factory template duplicates are used from the ./macos folder)
    charttype = "auto"

    if len(sys.argv) > 1:
        param = sys.argv[1]

    if len(sys.argv) > 2:
        charttype = sys.argv[2]
        if charttype != "orgchart" and charttype != "radial" and charttype != "auto":
            print("Invalid chart type. Use 'orgchart' or 'radial'.")
            sys.exit(1)
        
    try:
        main(param, charttype)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
