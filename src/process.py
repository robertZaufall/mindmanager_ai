#!/usr/bin/env python3
import gc
import config
import prompts

import mermaid_helper
import file_helper
import input_helper

import sys
import os
import uuid

import ai_llm
import ai_image
import ai_translation

if sys.platform.startswith('win'):
    import mindmanager.mindmanager_win as mindmanager
    platform = "win"
elif sys.platform.startswith('darwin'):
    import mindmanager.mindmanager_mac as mindmanager
    platform = "darwin"

def recurse_topics(mindm, mermaid_diagram, this_topic, level):
    this_topic_text = mindm.get_title_from_topic(this_topic)
    if level == 0:
        top_level = mermaid_helper.get_mermaid_line(0, this_topic_text)
        mermaid_diagram = recurse_topics(mindm, top_level, this_topic, 1)
        return mermaid_diagram
    if level > 1:
        mermaid_diagram += mermaid_helper.get_mermaid_line(level, this_topic_text)
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
    mermaid_topics = mermaid_helper.parse_mermaid(mermaid_diagram, config.LINE_SEPARATOR, config.INDENT_SIZE)
    max_topic_level = max(topic.topic_level for topic in mermaid_topics)
    return (mermaid_topics, max_topic_level)

def create_new_map_from_mermaid(mindm, mermaid_diagram):
    (mermaid_topics, max_topic_level) = get_mermaid_topics(mindm, mermaid_diagram)
    mindm.add_document(max_topic_level)
    parent_topic = mindm.get_central_topic()
    mindm.set_title_to_topic(parent_topic, mermaid_topics[0].topic_text)
    create_sub_topics(mindm, mermaid_topics, 1, mindm.get_central_topic())
    return max_topic_level

def create_map_and_finalize(mindm, new_mermaid_diagram):
    if new_mermaid_diagram != "":
        max_topic_level = create_new_map_from_mermaid(mindm, new_mermaid_diagram)
        mindm.finalize(max_topic_level)

def get_topic_texts(mindm):
    central_topic_selected = False
    selection = mindm.get_selection()
    topic_texts = []
    topic_levels = []
    if len(selection) > 0:
        for this_topic in selection:
            if mindm.get_level_from_topic(this_topic) > 0:
                topic_texts.append(mindm.get_title_from_topic(this_topic))
                topic_levels.append(mindm.get_level_from_topic(this_topic))
            else:
                central_topic_selected = True
    return topic_texts, topic_levels, central_topic_selected

def generate_glossary_html(content, guid):
    file_path = file_helper.get_new_file_paths("docs", guid)
    try:
        import markdown
        html_fragment = markdown.markdown(content)
    except Exception as e:
        with open(file_path + ".error", 'w') as f:
            f.write(f'caught {str(e)}: e') 
        raise
    template = get_template_content("glossary.html")
    html = template.replace("{{title}}", "Glossary").replace("{{body}}", html_fragment.replace("</h2>", "</h2><hr/>"))
    with open(file_path, 'w') as f:
        f.write(html)
    file_helper.open_file(file_path, platform)

def generate_argumentation_html(content, guid):
    file_path = file_helper.get_new_file_paths("docs", guid)
    try:
        import markdown
        html_fragment = markdown.markdown(content)
    except Exception as e:
        with open(file_path + ".error", 'w') as f:
            f.write(f'caught {str(e)}: e') 
        raise
    template = get_template_content("argumentation.html")
    html = template.replace("{{title}}", "Notes").replace("{{body}}", html_fragment.replace("</h2>", "</h2><hr/>"))
    with open(file_path, 'w') as f:
        f.write(html)
    file_helper.open_file(file_path, platform)

def generate_markmap_html(content, max_topic_level, guid):
    file_path = file_helper.get_new_file_paths("docs", guid)
    this_content = config.MARKMAP_TEMPLATE.replace("{{colorFreezeLevel}}", str(max_topic_level)).replace("{{markmap}}", content)
    template = get_template_content("markmap.html")
    html = template.replace("{{body}}", this_content).replace("{{title}}", "Markmap")
    with open(file_path, 'w') as f:
        f.write(html)
    file_helper.open_file(file_path, platform)

def generate_mermaid_html(content, max_topic_level, guid, open_file = True):
    file_path = file_helper.get_new_file_paths("docs", guid)
    this_content = config.MERMAID_TEMPLATE.replace("{{mermaid}}", content)
    template = get_template_content("mermaid.html")
    html = template.replace("{{body}}", this_content).replace("{{title}}", "Mermaid")
    with open(file_path, 'w') as f:
        f.write(html)
    if open_file:
        file_helper.open_file(file_path, platform)

def get_template_content(template_name):
    templates_folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "templates")
    with open(os.path.join(templates_folder_path, template_name), 'r') as f:
        template = f.read()
    return template

def generate_image(mindm, central_topic, topic_texts, central_topic_selected, guid, topic_levels):
    central_topic_text = mindm.get_title_from_topic(central_topic)
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

    folder_path_images = file_helper.create_folder_if_not_exists(os.path.join(mindm.library_folder, "Images"), top_most_topic)
    file_name = f"{guid}.png"
    file_path = os.path.join(folder_path_images, file_name)      

    if "image" in param:
        count = param.split("_")[-1]
        if count.isdigit():
            count = int(count)
        else:
            count = 1

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
            mindm.set_document_background_image(image_path)
        else:
            from PIL import Image
            image = Image.open(image_path)  
            image.show()


def main(param, charttype):
    mindm = mindmanager.Mindmanager(charttype)

    if param.startswith("pdf_"):
        actions = param.split("_")[-1].split("+")
        docs = input_helper.load_pdf_files(optimization_level=config.MARKDOWN_OPTIMIZATION_LEVEL)
        for key, value in docs.items():
            if "mindmap" in actions:
                new_mermaid_diagram = ai_llm.call_llm_sequence(["text2mindmap"], value, topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " "))
                create_map_and_finalize(mindm, new_mermaid_diagram)
            if "knowledgegraph" in actions:
                guid = uuid.uuid4()
                mermaid_diagram = ai_llm.call_llm_sequence(["text2knowledgegraph"], value, topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " "))
                content, max_topic_level = mermaid_helper.export_to_mermaid(mermaid_diagram, False)
                generate_mermaid_html(content, max_topic_level, guid, False)
                new_mermaid_diagram = ai_llm.call_llm_sequence(["knowledgegraph2mindmap"], content, topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " "))
                create_map_and_finalize(mindm, new_mermaid_diagram)
    
    elif param.startswith("pdfsimple"):
        actions = param.split("_")[-1].split("+")
        if "application/pdf" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdfsimple_files()
            for key, value in docs.items():
                if "mindmap" in actions:
                    new_mermaid_diagram = ai_llm.call_llm_sequence(["pdfsimple2mindmap"], "", topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " "), data=value, mimeType="application/pdf")
                    create_map_and_finalize(mindm, new_mermaid_diagram)
        elif "image/png" in config.MULTIMODAL_MIME_TYPES:
            docs = input_helper.load_pdf_files(optimization_level=0, as_images=True, as_images_dpi=config.MULTIMODAL_PDF_TO_IMAGE_DPI, mime_type="image/png", as_base64=True)
            for key, value in docs.items():
                if "mindmap" in actions:
                    new_mermaid_diagram = ai_llm.call_llm_sequence(["pdfsimple2mindmap"], "", topic_texts=key.replace(".pdf", "").replace("_", " ").replace("-", " "), data=value, mimeType="image/png")
                    create_map_and_finalize(mindm, new_mermaid_diagram)
        else:
            raise Exception("PDF Simple is not supported for this multimodal AI model.")

    elif param.startswith("import_"):
        actions = param.split("_")[-1]
        if actions == "md":
            docs = input_helper.load_text_files("md")
            for key, value in docs.items():
                new_mermaid_diagram = ai_llm.call_llm_sequence(["md2mindmap"], value, topic_texts=key.replace(".md", "").replace("_", " ").replace("-", " "))
                create_map_and_finalize(mindm, new_mermaid_diagram)
    else:
        if not mindm.document_exists():
            print("No document found.")    
            return

        central_topic = mindm.get_central_topic()
        mermaid_diagram = recurse_topics(mindm, "", central_topic, 0)

        if param == "finalize":
        
            if platform == "win":
                max_topic_level = get_mermaid_topics(mindm, mermaid_diagram)[1]
            else:
                max_topic_level = create_new_map_from_mermaid(mindm, mermaid_diagram)
            mindm.finalize(max_topic_level)

        else:
            prompts_list = prompts.prompts_list_from_param(param)

            if mindm.document_exists():
                topic_texts = []
                if len(prompts_list) == 1:
                    topic_texts, topic_levels, central_topic_selected = get_topic_texts(mindm)

                guid = uuid.uuid4()
                if "image" in param:
                    generate_image(mindm, central_topic, topic_texts, central_topic_selected, guid, topic_levels)

                elif param == "glossary":
                    markdown = ai_llm.call_llm_sequence(prompts_list, mermaid_diagram, topic_texts=",".join(topic_texts), check_valid_mermaid=False)
                    if "-mini" in config.CLOUD_TYPE or \
                        "GROQ+llama-3.1-8b" in config.CLOUD_TYPE or \
                        ("MLX+" in config.CLOUD_TYPE and "Llama-3.1-8B" in config.CLOUD_TYPE):
                        # take an optimization round
                        markdown = ai_llm.call_llm(prompts.prompt_glossary_optimize(markdown))
                    generate_glossary_html(markdown, guid)

                elif param == "argumentation":
                    markdown = ai_llm.call_llm_sequence(prompts_list, mermaid_diagram, topic_texts=",".join(topic_texts), check_valid_mermaid=False)
                    generate_argumentation_html(markdown, guid)

                elif param == "export_markmap":
                    content, max_topic_level = mermaid_helper.export_to_markmap(mermaid_diagram)
                    generate_markmap_html(content, max_topic_level, guid)

                elif param == "export_mermaid":
                    content, max_topic_level = mermaid_helper.export_to_mermaid(mermaid_diagram)
                    generate_mermaid_html(content, max_topic_level, guid)

                elif "translate_deepl" in param:
                    language = param.split("+")[-1]
                    new_mermaid_diagram = ai_translation.call_translation_ai(mermaid_diagram, language)
                    create_map_and_finalize(mindm, new_mermaid_diagram)

                else:
                    new_mermaid_diagram = ai_llm.call_llm_sequence(prompts_list, mermaid_diagram, topic_texts=",".join(topic_texts))
                    create_map_and_finalize(mindm, new_mermaid_diagram)

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
