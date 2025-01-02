#!/usr/bin/env python3
import gc
import config
import ai.prompts as prompts

from mindmap.mindmap_helper import *
from mermaid.mermaid_helper import *
import mermaid.mermaid_helper as mermaid_helper

import file_helper
import input_helper

import sys
import os
import uuid

import ai.ai_llm as ai_llm
import ai.ai_image as ai_image
import ai.ai_translation as ai_translation

if sys.platform.startswith('win'):
    platform = "win"
elif sys.platform.startswith('darwin'):
    platform = "darwin"

def create_sub_topics(mermaid_topics, index, parent_topic): # MindmapTopic
    i = index
    parent_topic_level = parent_topic.topic_level
    last_topic = None
    while i < len(mermaid_topics):
        topic_level = mermaid_topics[i].topic_level
        topic_text = mermaid_topics[i].topic_text
        if topic_level <= parent_topic_level: 
            return i
        if topic_level == parent_topic_level + 1:
            new_topic = MindmapTopic(topic_text=topic_text, topic_level=topic_level, topic_subtopics=[])
            parent_topic.topic_subtopics.append(new_topic)
            last_topic = new_topic
        if topic_level > parent_topic_level + 1:
            i = create_sub_topics(mermaid_topics, i, last_topic) - 1
        i += 1
    return i

def create_new_map_from_mermaid(document, mermaid):
    mermaid_topics = mermaid.mermaid_topics
    parent_topic = MindmapTopic(topic_text=mermaid_topics[0].topic_text, topic_level=0)
    create_sub_topics(mermaid_topics, 1, parent_topic)
    document.mindmap = parent_topic

def create_map_and_finalize(document, mermaid):
    if mermaid.mermaid_mindmap != "":
        create_new_map_from_mermaid(document, mermaid)
        max_topic_level = document.get_max_topic_level(document.mindmap)
        document.create_mindmap_and_finalize([], max_topic_level)

def generate_image(document, topic_texts, central_topic_selected, guid, topic_levels, count=1):
    central_topic_text = document.mindmap.topic_text
    subtopics = ""
    if len(topic_texts) == 0: 
        top_most_topic = central_topic_text
    else:
        if central_topic_selected:
            top_most_topic = central_topic_text
            subtopics =  ",".join(topic_texts)
        else:
            min_level = min(topic_levels)
            max_level = max(topic_levels)
            if (min_level == max_level):
                top_most_topic = central_topic_text
                subtopics =  ",".join(topic_texts)
            else:
                top_most_topic = ""
                for i in range(len(topic_levels)):
                    if topic_levels[i] != max_level:
                        top_most_topic += topic_texts[i] + "/"
                    else:
                        subtopics += topic_texts[i] + ","

                if top_most_topic.endswith("/"):
                    top_most_topic = top_most_topic[:-1]
                if subtopics.endswith(","):
                    subtopics = subtopics[:-1]

    folder_path_images = file_helper.create_folder_if_not_exists(os.path.join(document.get_library_folder(), "Images"), top_most_topic)
    file_name = f"{guid}.png"
    file_path = os.path.join(folder_path_images, file_name)      

    if "MLX+" in config.CLOUD_TYPE_IMAGE:
        if "flux" in config.IMAGE_MODEL_ID:
            str_user = prompts.prompt_image_flux(top_most_topic, subtopics)
        else:
            str_user = prompts.prompt_image_sd(top_most_topic, subtopics)
    else:
        str_user = prompts.prompt_image_flux(top_most_topic, subtopics) # prompts.prompt_image(top_most_topic, subtopics)
    if ("STABILITYAI+" in config.CLOUD_TYPE_IMAGE) and config.OPTIMIZE_PROMPT_IMAGE:
        final_prompt = ai_llm.call_llm(prompts.prompt_image_prompt(str_user))
    else:
        final_prompt = str_user

    image_path = ai_image.call_image_ai(file_path, final_prompt, count)

    if config.INSERT_IMAGE_AS_BACKGROUND and central_topic_selected and platform == "win":
        document.set_background_image(image_path)
    else:
        from PIL import Image
        image = Image.open(image_path)  
        image.show()


def main(param, charttype):
    line_separator = config.LINE_SEPARATOR
    indent_size = config.INDENT_SIZE

    document = MindmapDocument(charttype=charttype)

    if param.startswith("pdf_"):
        actions = param.split("_")[-1].split("+")
        docs = input_helper.load_pdf_files(optimization_level=config.MARKDOWN_OPTIMIZATION_LEVEL)
        for key, value in docs.items():
            if "mindmap" in actions:
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(["text2mindmap"], value, topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " ")))
                create_map_and_finalize(document, mermaid)
            if "knowledgegraph" in actions:
                guid = uuid.uuid4()
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(["text2knowledgegraph"], value, topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " ")))
                content, max_topic_level = mermaid.export_to_mermaid(False)
                file_helper.generate_mermaid_html(content, max_topic_level, guid, False)
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(["knowledgegraph2mindmap"], content, topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " ")))
                create_map_and_finalize(document, mermaid)
    
    elif param.startswith("pdfsimple"):
        actions = param.split("_")[-1].split("+")
        if "application/pdf" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdfsimple_files()
            for key, value in docs.items():
                if "mindmap" in actions:
                    mermaid = MermaidMindmap(ai_llm.call_llm_sequence(["pdfsimple2mindmap"], "", topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " "), data=value, mimeType="application/pdf"))
                    create_map_and_finalize(document, mermaid)
        elif "image/png" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdf_files(optimization_level=0, as_images=True, as_images_dpi=config.MULTIMODAL_PDF_TO_IMAGE_DPI, mime_type="image/png", as_base64=True)
            for key, value in docs.items():
                if "mindmap" in actions:
                    mermaid = MermaidMindmap(ai_llm.call_llm_sequence(["pdfsimple2mindmap"], "", topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " "), data=value, mimeType="image/png"))
                    create_map_and_finalize(document, mermaid)
        else:
            raise Exception("PDF Simple is not supported for this multimodal AI model.")

    elif param.startswith("import_"):
        actions = param.split("_")[-1]
        if actions == "md":
            docs = input_helper.load_text_files("md")
            for key, value in docs.items():
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(["md2mindmap"], value, topic_texts=key.replace(".md", "").replace("_", " ").replace("-", " ")))
                create_map_and_finalize(document, mermaid)
    else:
        if not document.get_mindmap():
            return
        
        mermaid = MermaidMindmap(recurse_topics("", document.mindmap, 0))
        
        if param == "finalize":
        
            if platform == "win":
                max_topic_level = mermaid.mermaid_topics[1]
            else:
                create_new_map_from_mermaid(mermaid)
                max_topic_level = mermaid.max_topic_level
            document.finalize(max_topic_level)

        else:
            prompts_list = prompts.prompts_list_from_param(param)

            topic_texts = []
            if len(prompts_list) == 1:
                topic_texts = document.selected_topic_texts
                topic_levels = document.selected_topic_levels
                central_topic_selected = document.central_topic_selected

            guid = uuid.uuid4()
            if "image" in param:
                count = param.split("_")[-1]
                if count.isdigit():
                    count = int(count)
                else:
                    count = 1
                generate_image(document, topic_texts, central_topic_selected, guid, topic_levels, count)

            elif param == "glossary":
                markdown = ai_llm.call_llm_sequence(prompts_list, mermaid.mermaid_mindmap, topic_texts=",".join(topic_texts), check_valid_mermaid=False)
                if "-mini" in config.CLOUD_TYPE or \
                    "GROQ+llama-3.1-8b" in config.CLOUD_TYPE or \
                    ("MLX+" in config.CLOUD_TYPE and "Llama-3.1-8B" in config.CLOUD_TYPE):
                    # take an optimization round
                    markdown = ai_llm.call_llm(prompts.prompt_glossary_optimize(markdown))
                file_helper.generate_glossary_html(markdown, guid)

            elif param == "argumentation":
                markdown = ai_llm.call_llm_sequence(prompts_list, mermaid.mermaid_mindmap, topic_texts=",".join(topic_texts), check_valid_mermaid=False)
                file_helper.generate_argumentation_html(markdown, guid)

            elif param == "export_markmap":
                content, max_topic_level = mermaid.export_to_markmap()
                file_helper.generate_markmap_html(content, max_topic_level, guid)

            elif param == "export_mermaid":
                content, max_topic_level = mermaid.export_to_mermaid()
                file_helper.generate_mermaid_html(content, max_topic_level, guid)

            elif "translate_deepl" in param:
                language = param.split("+")[-1]
                mermaid = MermaidMindmap(ai_translation.call_translation_ai(mermaid.mermaid_mindmap, language))
                create_map_and_finalize(document, mermaid)

            else:
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(prompts_list, mermaid.mermaid_mindmap, topic_texts=",".join(topic_texts)))
                create_map_and_finalize(document, mermaid)

    print("Done.")

if __name__ == "__main__":
    
    allocs, g1, g2 = gc.get_threshold()
    gc.set_threshold(allocs*100, g1*5, g2*10)

    # refine, refine_dev
    # complexity_1, complexity_2, complexity_3
    # examples, cluster, exp, capex_opex
    # prc_org, prj_prc_org, exp_prj_prc_org, prj_org
    # finalize (no llm call - just existing (win) or new map (macos) with defined charttype / formattings)
    # image (experimental)
    # image_nn (experimental)
    # translate_deepl+EN-US, translate_deepl+DE, ...
    # glossary
    # export_markmap, export_mermaid
    # pdf_mindmap
    # pdf_knowledgegraph
    # pdfsimple_mindmap
    # import_md
    # news
    # argumentation
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
    
    if param.startswith("pdf_") and charttype == "auto":
        charttype = "radial"

    try:
        main(param, charttype)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
