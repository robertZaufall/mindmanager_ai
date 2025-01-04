#!/usr/bin/env python3
import gc
import config as cfg
import ai.prompts as prompts

from mindmap.mindmap_helper import *
from mermaid.mermaid_helper import *
import mermaid.mermaid_helper as mermaid_helper

import file_helper
import input_helper
import text_helper

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

valid_actions = [
    "refine", "refine_dev", 
    "complexity_1", "complexity_2", "complexity_3", 
    "examples", "cluster", "exp", "capex_opex", 
    "prc_org", "prj_prc_org", "exp_prj_prc_org", "prj_org", 
    "finalize", # (no llm call - just existing (win) or new map (macos) with defined charttype / formattings)
    "image", "image_5", "image_10", 
    "translate_deepl+EN-US", "translate_deepl+DE", 
    "glossary", "argumentation",
    "export_markmap", "export_mermaid", 
    "pdf_mindmap", "pdf_knowledgegraph", "pdfsimple_mindmap", 
    "import_md", 
    "news",
    "freetext"
]

valid_charttypes = ["orgchart", "radial", "auto"] # (-> on macos factory template duplicates are used from the ./macos folder)

def create_mindmap_from_mermaid(document, mermaid):
    charttype = document.charttype
    document = MindmapDocument(charttype=charttype)
    if mermaid.mermaid_mindmap != "":
        document.mindmap = mermaid.create_mindmap_from_mermaid()
        document.max_topic_level = document.get_max_topic_level(document.mindmap)
        document.create_mindmap_and_finalize([])
        document.mindmap = None
        document.mindm = None
        document.selection = None

def generate_image(model, document, topic_texts, central_topic_selected, guid, topic_levels, count=1):

    config = cfg.get_image_config(model)

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

    folder_path_images = file_helper.create_folder_if_not_exists(root_path=os.path.join(document.get_library_folder(), "Images"), central_topic_text=top_most_topic)
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
        final_prompt = ai_llm.call_llm(model=model, str_user=prompts.prompt_image_prompt(str_user))
    else:
        final_prompt = str_user

    image_path = ai_image.call_image_ai(model=model, image_path=file_path, str_user=final_prompt, n_count=count)

    if config.INSERT_IMAGE_AS_BACKGROUND and central_topic_selected and platform == "win":
        document.set_background_image(image_path)
    else:
        from PIL import Image
        image = Image.open(image_path)  
        image.show()


def main(param, charttype, model, freetext):

    document = None
    mermaid = None

    if "image" in param:
        if model == "":
            model = cfg.CLOUD_TYPE_IMAGE
        config = cfg.get_image_config(model)
    else:
        if model == "":
            model = cfg.CLOUD_TYPE
        config = cfg.get_config(model)

    if param.startswith("pdf_") and charttype == "auto":
        charttype = "radial"

    document = MindmapDocument(charttype=charttype)
    mermaid = MermaidMindmap("")

    if param.startswith("pdf_"):
        actions = param.split("_")[-1].split("+")
        docs = input_helper.load_pdf_files(optimization_level=config.MARKDOWN_OPTIMIZATION_LEVEL)
        for key, value in docs.items():
            key_plain = text_helper.cleanse_title(key)
            if "mindmap" in actions:
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(model=model, prompts_list=["text2mindmap"], input=value, topic_texts=key_plain))
                create_mindmap_from_mermaid(document, mermaid)
            if "knowledgegraph" in actions:
                guid = uuid.uuid4()
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(model=model, prompts_list=["text2knowledgegraph"], input=value, topic_texts=key_plain))
                content, max_topic_level = mermaid.export_to_mermaid(False)
                file_helper.generate_mermaid_html(content, max_topic_level, guid, False)
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(model=model, prompts_list=["knowledgegraph2mindmap"], input=content, topic_texts=key_plain))
                create_mindmap_from_mermaid(document, mermaid)
    
    elif param.startswith("pdfsimple"):
        actions = param.split("_")[-1].split("+")
        if "application/pdf" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdfsimple_files()
            for key, value in docs.items():
                if "mindmap" in actions:
                    mermaid = MermaidMindmap(ai_llm.call_llm_sequence(model=model, prompts_list=["pdfsimple2mindmap"], input="", topic_texts=text_helper.cleanse_title(key), data=value, mimeType="application/pdf"))
                    create_mindmap_from_mermaid(document, mermaid)
        elif "image/png" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdf_files(optimization_level=0, as_images=True, as_images_dpi=config.MULTIMODAL_PDF_TO_IMAGE_DPI, mime_type="image/png", as_base64=True)
            for key, value in docs.items():
                if "mindmap" in actions:
                    mermaid = MermaidMindmap(ai_llm.call_llm_sequence(model=model, prompts_list=["pdfsimple2mindmap"], input="", topic_texts=text_helper.cleanse_title(key), data=value, mimeType="image/png"))
                    create_mindmap_from_mermaid(document, mermaid)
        else:
            raise Exception("PDF Simple is not supported for this multimodal AI model.")

    elif param.startswith("import_"):
        actions = param.split("_")[-1]
        if actions == "md":
            docs = input_helper.load_text_files("md")
            for key, value in docs.items():
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(model=model, prompts_list=["md2mindmap"], input=value, topic_texts=text_helper.cleanse_title(key)))
                create_mindmap_from_mermaid(document, mermaid)
    else:

        # load DOM
        if not document.get_mindmap():
            print("DOM could not be loaded.")
            sys.exit(1)
                
        if param == "finalize":
            if platform == "win":
                document.finalize()
            else:
                document.create_mindmap([])

        else:
            mermaid = MermaidMindmap(get_mermaid_from_mindmap(document.mindmap))
            prompts_list = prompts.prompts_list_from_param(param)

            topic_texts = []
            if len(prompts_list) == 1:
                topic_texts = document.selected_topic_texts
                topic_levels = document.selected_topic_levels
                central_topic_selected = document.central_topic_selected
            topic_texts_join = ",".join(topic_texts) if len(topic_texts) > 0 else ""

            guid = uuid.uuid4()
            if "image" in param:
                count = param.split("_")[-1]
                if count.isdigit():
                    count = int(count)
                else:
                    count = 1
                generate_image(model, document, topic_texts, central_topic_selected, guid, topic_levels, count)

            elif param == "glossary":
                markdown = ai_llm.call_llm_sequence(model=model, prompts_list=prompts_list, input=mermaid.mermaid_mindmap, topic_texts=topic_texts_join)
                if "-mini" in config.CLOUD_TYPE or \
                    "GROQ+llama-3.1-8b" in config.CLOUD_TYPE or \
                    ("MLX+" in config.CLOUD_TYPE and "Llama-3.1-8B" in config.CLOUD_TYPE):
                    # take an optimization round
                    markdown = ai_llm.call_llm(model=model, str_user=prompts.prompt_glossary_optimize(markdown))
                file_helper.generate_glossary_html(markdown, guid)

            elif param == "argumentation":
                markdown = ai_llm.call_llm_sequence(model=model, prompts_list=prompts_list, input=mermaid.mermaid_mindmap, topic_texts=topic_texts_join)
                file_helper.generate_argumentation_html(markdown, guid)

            elif param == "export_markmap":
                content, max_topic_level = mermaid.export_to_markmap()
                file_helper.generate_markmap_html(content, max_topic_level, guid)

            elif param == "export_mermaid":
                content, max_topic_level = mermaid.export_to_mermaid()
                file_helper.generate_mermaid_html(content, max_topic_level, guid)

            elif "translate_deepl" in param:
                language = param.split("+")[-1]
                mermaid = MermaidMindmap(ai_translation.call_translation_ai(text=mermaid.mermaid_mindmap, language=language))
                create_mindmap_from_mermaid(document, mermaid)

            else:
                mermaid = MermaidMindmap(ai_llm.call_llm_sequence(model=model, prompts_list=prompts_list, input=mermaid.mermaid_mindmap, topic_texts=topic_texts_join))
                create_mindmap_from_mermaid(document, mermaid)

    del document
    del mermaid
    gc.collect()

    print("Done.")

def validate_input(param, charttype, model, freetext):
    if param not in valid_actions:
        print("Invalid action. Use one of the following: " + ", ".join(valid_actions))
        sys.exit(1)

    if charttype not in valid_charttypes:
        print("Invalid charttype. Use one of the following: " + ", ".join(valid_charttypes))
        sys.exit(1)

    if freetext != "" and param != "freetext":
        print("Invalid action. Use 'freetext' only with the 'freetext' action.")
        sys.exit(1)

    return param, charttype, model, config

def ui_main(payload):
    param = payload["action"]
    model = payload["model"]
    data = payload["data"]
    settings = payload["settings"]
    freetext = data.get("freetext", "")
    charttype = settings["chartType"]
    modify_map = settings["modifyLiveMap"]

    validate_input(param, charttype, model, freetext)

    try:
        main(param, charttype, model, freetext)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    allocs, g1, g2 = gc.get_threshold()
    gc.set_threshold(allocs*100, g1*5, g2*10)
    
    param = "refine" 
    charttype = "auto"
    model = ""
    freetext = ""

    if len(sys.argv) > 1:
        param = sys.argv[1]

    if len(sys.argv) > 2:
        charttype = sys.argv[2]
    
    if len(sys.argv) > 3:
        model = sys.argv[3] # overwrite model from config
    
    if len(sys.argv) > 4:
        freetext = sys.argv[4]

    validate_input(param, charttype, model, freetext)

    try:
        main(param, charttype, model, freetext)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
