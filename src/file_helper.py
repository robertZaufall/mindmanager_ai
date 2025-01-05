import re
import os
import sys

import config as cfg

config = cfg.get_config()

if sys.platform.startswith('win'):
    platform = "win"
elif sys.platform.startswith('darwin'):
    platform = "darwin"

def sanitize_folder_name(folder_name):
    folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name)
    folder_name = folder_name.strip('. ')
    folder_name = re.sub(r'[ .]', '_', folder_name)
    if not folder_name:
        folder_name = "unnamed_folder"
    folder_name = folder_name[:255]
    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]
    if folder_name.upper() in reserved_names:
        folder_name = "_" + folder_name
    return folder_name

def create_folder_if_not_exists(root_path, central_topic_text):
    folder_path = os.path.join(root_path, f"⚡️{sanitize_folder_name(central_topic_text)}")
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    return folder_path

def open_file(file_path, platform):
    if platform == "darwin":
        os.system(f"open {file_path}")
    if platform == "win":
        import subprocess
        subprocess.Popen(f'cmd /k start explorer.exe "{file_path}"', shell=False)

def get_new_file_paths(folder_name, guid):
    doc_folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), folder_name)
    if not os.path.exists(doc_folder_path): os.makedirs(doc_folder_path)
    file_name = f"{guid}.html"
    file_path = os.path.join(doc_folder_path, file_name)
    return file_path

def generate_glossary_html(content, guid):
    file_path = get_new_file_paths("docs", guid)
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
    open_file(file_path, platform)

def generate_argumentation_html(content, guid):
    file_path = get_new_file_paths("docs", guid)
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
    open_file(file_path, platform)

def generate_markmap_html(content, max_topic_level, guid):
    file_path = get_new_file_paths("docs", guid)
    this_content = config.MARKMAP_TEMPLATE \
                        .replace("{{colorFreezeLevel}}", str(max_topic_level)) \
                        .replace("{{markmap}}", content)
    template = get_template_content("markmap.html")
    html = template.replace("{{body}}", this_content).replace("{{title}}", "Markmap")
    with open(file_path, 'w') as f:
        f.write(html)
    open_file(file_path, platform)

def generate_mermaid_html(content, max_topic_level, guid, do_open_file = True):
    file_path = get_new_file_paths("docs", guid)
    this_content = config.MERMAID_TEMPLATE.replace("{{mermaid}}", content)
    template = get_template_content("mermaid.html")
    html = template.replace("{{body}}", this_content).replace("{{title}}", "Mermaid")
    with open(file_path, 'w') as f:
        f.write(html)
    if do_open_file:
        open_file(file_path, platform)

def get_template_content(template_name):
    templates_folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "templates")
    with open(os.path.join(templates_folder_path, template_name), 'r') as f:
        template = f.read()
    return template

def log_input_output(input, output, prompt):
    try:
        folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "log")
        if not os.path.exists(folder_path): os.makedirs(folder_path)        
        with open(folder_path + "/input.txt", "w", encoding='utf-8', errors='ignore') as file:
            file.write(input)
        with open(folder_path + "/output.txt", "w", encoding='utf-8') as file:
            file.write(output)
        with open(folder_path + "/prompt.txt", "w", encoding='utf-8') as file:
            file.write(prompt)
    except Exception as e:
        print(f"Error writing log files: {str(e)}")