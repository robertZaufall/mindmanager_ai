#!/usr/bin/env python3
import gc
import config_llm as cfg
import config_image as cfg_image
import config_translate as cfg_translate
import ai.prompts as prompts

from mindmap.mindmap import MindmapDocument

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
import ai.ai_agent as ai_agent

if sys.platform.startswith('win'):
    platform = "win"
elif sys.platform.startswith('darwin'):
    platform = "darwin"

valid_actions = [
    "refine", "refine_dev", "refine_grounding", 
    "complexity_1", "complexity_2", "complexity_3", 
    "examples", "cluster", "exp", "capex_opex", 
    "prc_org", "prj_prc_org", "exp_prj_prc_org", "prj_org", 
    "finalize", # (no llm call - just existing (win) or new map (macos) with defined charttype / formattings)
    "image", "image_5", "image_10", 
    #"translate_deepl+EN-US", "translate_deepl+DE", 
    "glossary", "argumentation",
    "export_markmap", "export_mermaid", 
    "pdf_mindmap", "pdf_knowledgegraph", "pdfsimple_mindmap", 
    "import_md", 
    "news",
    "freetext",
    "agent"
]

valid_charttypes = ["orgchart", "radial", "auto"] # (-> on macos factory template duplicates are used from the ./macos folder)


def create_mindmap_from_mermaid(document, mermaid, inplace=False):
    charttype = document.charttype
    turbo_mode = document.turbo_mode
    document = MindmapDocument(charttype=charttype, turbo_mode=turbo_mode)
    if mermaid.mermaid_mindmap != "":
        document.mindmap = mermaid.create_mindmap_from_mermaid()
        document.max_topic_level = document.get_max_topic_level(mindmap_topic=document.mindmap)
        document.create_mindmap_and_finalize()
        document.mindmap = None
        document.mindm = None


def generate_image(model, document, guid, count=1):

    config = cfg_image.get_image_config(model)

    # collect some grounding information for LLM
    top_most_topic, subtopics = document.get_grounding_information()

    # store images in the library under images and background images
    file_paths = file_helper.get_image_file_paths(library_folder=document.get_library_folder(), top_most_topic=top_most_topic, guid=guid)
    
    if "MLX+" in config.CLOUD_TYPE_IMAGE:
        if "flux" in config.IMAGE_MODEL_ID:
            str_user = prompts.prompt_image_flux(top_most_topic, subtopics)
        else:
            str_user = prompts.prompt_image_sd(top_most_topic, subtopics)
    else:
        str_user = prompts.prompt_image_flux(top_most_topic, subtopics) # prompts.prompt_image(top_most_topic, subtopics)
    if ("STABILITYAI+" in config.CLOUD_TYPE_IMAGE) and config.OPTIMIZE_PROMPT_IMAGE:
        final_prompt = ai_llm.call_llm(model=model, str_user=prompts.prompt_image_prompt(str_user), param="image")
    else:
        final_prompt = str_user

    image_paths = ai_image.call_image_ai(model=model, image_paths=file_paths, str_user=final_prompt, n_count=count)

    if config.INSERT_IMAGE_AS_BACKGROUND and document.central_topic_selected and platform == "win":
        document.set_background_image(image_paths[1])
    else:
        from PIL import Image
        image = Image.open(image_paths[0])  
        image.show()


def main(param, charttype, model, freetext, inplace=False):

    document = None
    mermaid = None

    if "image" in param:
        if model == "":
            model = cfg_image.CLOUD_TYPE_IMAGE
        config = cfg_image.get_image_config(model)
    elif param.startswith("translate_deepl"):
        if model == "":
            model = cfg_translate.CLOUD_TYPE_TRANSLATION
        config = cfg_translate.get_translation_config(model)
    elif param.startswith("translate_llm"):
        if model == "":
            model = cfg.CLOUD_TYPE
        config = cfg.get_config(model)
    else:
        if model == "":
            model = cfg.CLOUD_TYPE
        secondary_model = model.split("|")[1] if "|" in model else ""
        model = model.split("|")[0]
        config = cfg.get_config(model)

    if param.startswith("pdf_") and charttype == "auto":
        charttype = "radial"

    document = MindmapDocument(charttype=charttype, turbo_mode=config.TURBO_MODE)
    mermaid = MermaidMindmap("")

    # PDF import
    if param.startswith("pdf_"):
        actions = param.split("_")[-1].split("+")
        docs = input_helper.load_pdf_files(optimization_level=config.MARKDOWN_OPTIMIZATION_LEVEL)
        for key, value in docs.items():
            key_plain = text_helper.cleanse_title(key)

            # pdf to mindmap via text
            if "mindmap" in actions:
                mermaid = MermaidMindmap(
                    ai_llm.call_llm_sequence(model=model, params_list=["text2mindmap"], input=value, topic_texts=key_plain)
                )
                create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)

            # pdf to mindmap via text and (pseudo) knowledge graph (hint)
            if "knowledgegraph" in actions:
                guid = uuid.uuid4()

                # 1st call: pdf to knowledge graph
                mermaid = MermaidMindmap(
                    ai_llm.call_llm_sequence(model=model, params_list=["text2knowledgegraph"], input=value, topic_texts=key_plain)
                )
                content, max_topic_level = mermaid.export_to_mermaid(False)
                file_helper.generate_mermaid_html(content, max_topic_level, guid, False)

                # 2nd call: knowledge graph to mindmap
                mermaid = MermaidMindmap(
                    ai_llm.call_llm_sequence(model=model, params_list=["knowledgegraph2mindmap"], input=content, topic_texts=key_plain)
                )
                create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)
    
    elif param.startswith("pdfsimple"):
        actions = param.split("_")[-1].split("+")

        # PDF to mindmap multimodal: PDF
        if "application/pdf" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdfsimple_files()
            for key, value in docs.items():
                if "mindmap" in actions:
                    mermaid = MermaidMindmap(
                        ai_llm.call_llm_sequence(
                            model=model, 
                            params_list=["pdfsimple2mindmap"], 
                            input="", 
                            topic_texts=text_helper.cleanse_title(key), 
                            data=value, 
                            mimeType="application/pdf")
                    )
                    create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)

        # PDF to mindmap multimodal: image/png
        elif "image/png" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdf_files(optimization_level=0, as_images=True, as_images_dpi=config.MULTIMODAL_PDF_TO_IMAGE_DPI, mime_type="image/png", as_base64=True)
            for key, value in docs.items():
                if "mindmap" in actions:
                    mermaid = MermaidMindmap(
                        ai_llm.call_llm_sequence(
                            model=model, 
                            params_list=["pdfsimple2mindmap"], 
                            input="", 
                            topic_texts=text_helper.cleanse_title(key), 
                            data=value, 
                            mimeType="image/png"
                        )
                    )
                    create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)
        else:
            raise Exception("PDF Simple is not supported for this multimodal AI model.")

    elif param.startswith("import_"):
        actions = param.split("_")[-1]

        # markdown to mindmap
        if actions == "md":
            docs = input_helper.load_text_files("md")
            for key, value in docs.items():
                mermaid = MermaidMindmap(
                    ai_llm.call_llm_sequence(model=model, params_list=["md2mindmap"], input=value, topic_texts=text_helper.cleanse_title(key))
                )
                create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)

    else: # from here on a DOM is needed for content extraction

        # load DOM
        if not document.get_mindmap():
            print("DOM could not be loaded.")
            sys.exit(1)
        
        # reformat mindmap only
        if param == "finalize":
            if platform == "win":
                document.finalize()
            else:
                document.create_mindmap()

        else:
            mermaid = MermaidMindmap(get_mermaid_from_mindmap(mindmap=document.mindmap))
            params_list = prompts.prompts_list_from_param(param=param)
            topic_texts_join = ",".join(document.selected_topic_texts) if len(document.selected_topic_texts) > 0 else ""

            guid = uuid.uuid4()

            # Image generation
            if param.startswith("image"):
                count = param.split("_")[-1]
                if count.isdigit():
                    count = int(count)
                else:
                    count = 1
                generate_image(model, document, guid, count)

            elif param.startswith("agent+"):
                agent_action = param.split("+")[-1]
                argument = topic_texts_join if topic_texts_join != "" else document.mindmap.topic_text
                result = ai_agent.call_agent(agent_action, argument=argument, model=model, secondary_model=secondary_model)
                mermaid = MermaidMindmap(result)
                create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)

            # text generation: glossary in MD format
            elif param == "glossary":
                markdown = ai_llm.call_llm_sequence(model=model, params_list=params_list, input=mermaid.mermaid_mindmap, topic_texts=topic_texts_join)
                markdown = markdown[8:].strip() if markdown.startswith("markdown") else markdown
                if "GROQ+llama-3.1-8b" in config.CLOUD_TYPE or \
                    ("MLX+" in config.CLOUD_TYPE and "Llama-3.1-8B" in config.CLOUD_TYPE):
                    # take an optimization round
                    markdown = ai_llm.call_llm(model=model, str_user=prompts.prompt_glossary_optimize(markdown), param=param)
                file_helper.generate_glossary_html(markdown, guid)

            # text generation: argumentation in MD format
            elif param == "argumentation":
                markdown = ai_llm.call_llm_sequence(model=model, params_list=params_list, input=mermaid.mermaid_mindmap, topic_texts=topic_texts_join)
                markdown = markdown[8:].strip() if markdown.startswith("markdown") else markdown
                file_helper.generate_argumentation_html(markdown, guid)

            # mindmap to markmap
            elif param == "export_markmap":
                content, max_topic_level = mermaid.export_to_markmap()
                file_helper.generate_markmap_html(content, max_topic_level, guid)

            # mindmap to mermaid
            elif param == "export_mermaid":
                content, max_topic_level = mermaid.export_to_mermaid()
                file_helper.generate_mermaid_html(content, max_topic_level, guid)

            # translation
            elif "translate_deepl" in param:
                language = param.split("+")[-1]
                mermaid = MermaidMindmap(
                    ai_translation.call_translation_ai(text=mermaid.mermaid_mindmap, language=language)
                )
                create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)

            # mindmap to mindmap
            else:
                mermaid = MermaidMindmap(
                    ai_llm.call_llm_sequence(model=model, params_list=params_list, input=mermaid.mermaid_mindmap, topic_texts=topic_texts_join, freetext=freetext)
                )
                create_mindmap_from_mermaid(document=document, mermaid=mermaid, inplace=inplace)

    del document
    del mermaid
    gc.collect()

    print("Done.")

def validate_input(param, charttype, model, freetext):
    if param not in valid_actions and not param.startswith("translate_deepl+"):
        print("Invalid action. Use one of the following: " + ", ".join(valid_actions))
        sys.exit(1)

    if charttype not in valid_charttypes:
        print("Invalid charttype. Use one of the following: " + ", ".join(valid_charttypes))
        sys.exit(1)

    if freetext != "" and param != "freetext":
        print("Invalid action. Use 'freetext' only with the 'freetext' action.")
        sys.exit(1)

    return param, charttype, model

def ui_main(payload):
    param = payload["action"]
    model = payload["model"]
    data = payload["data"]
    settings = payload["settings"]
    freetext = data.get("freetext", "")
    agent_action = data.get("agent_action", "")
    model_strong = data.get("model_strong", "")
    model_cheap = data.get("model_cheap", "")
    charttype = settings["chartType"]
    inplace = settings["modifyLiveMap"]

    validate_input(param, charttype, model, freetext)

    if param == "agent":
        model = model_strong + "|" + model_cheap
        param = param + "+" + agent_action

    try:
        main(param=param, charttype=charttype, model=model, freetext=freetext, inplace=inplace)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    allocs, g1, g2 = gc.get_threshold()
    gc.set_threshold(allocs*100, g1*5, g2*10)
    
    param = "" 
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
