import tkinter as tk
from tkinter import ttk
import importlib
import process
import re
import os
import sys
import time
import process

ACTION_MAP = {
    "Refine": "refine",
    "Refine (Dev)": "refine_dev",
    "Examples": "examples",
    "Cluster": "cluster",
    "Glossary": "glossary",
    "Argumentation": "argumentation",
    "Translate to German": "translate_deepl+DE",
    "Translate to English": "translate_deepl+EN",
    "Image": "image",
    "Export markmap": "export_markmap",
    "Export mermaid": "export_mermaid",
    "Pdf to mindmap": "pdf_mindmap",
    "Pdf to mindmap (via knowledge graph)": "pdf_knowledgegraph",
    "Pdf simple (by image)": "pdfsimple_mindmap",
    "Import MD": "import_md"
}

def parse_cloud_definitions(filename):
    cloud_type_pattern = re.compile(r"CLOUD_TYPE\s*=\s*'([^']*)'")
    cloud_type_img_pattern = re.compile(r"CLOUD_TYPE_IMAGE\s*=\s*'([^']*)'")

    cloud_types = []
    uncommented_cloud_type = None
    cloud_images = []
    uncommented_cloud_image = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            match_type = cloud_type_pattern.search(line)
            if match_type:
                value = match_type.group(1).strip()
                if value:
                    cloud_types.append(value)
                    if not line.lstrip().startswith('#'):
                        uncommented_cloud_type = value
            
            match_img = cloud_type_img_pattern.search(line)
            if match_img:
                value = match_img.group(1).strip()
                if value:
                    cloud_images.append(value)
                    if not line.lstrip().startswith('#'):
                        uncommented_cloud_image = value

    return {
        'all_cloud_types': cloud_types,
        'active_cloud_type': uncommented_cloud_type,
        'all_cloud_images': cloud_images,
        'active_cloud_image': uncommented_cloud_image
    }

def call_process(*args):

    charttype = "auto"
    model = args[0]
    action = args[1]
    text = args[2]
    print(f"Process called with: {args}. Please wait...")
    root.update()
    root.update_idletasks()
    process.main(action, charttype, model, text)
    importlib.reload(process)

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.config(state='normal')
        self.text_widget.insert('end', string)
        self.text_widget.see('end')
        self.text_widget.config(state='disabled')

    def flush(self):
        pass

def main_ui():
    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.py'))
    data = parse_cloud_definitions(filename)

    all_cloud_types = data['all_cloud_types']
    active_cloud_type = data['active_cloud_type'] or (all_cloud_types[0] if all_cloud_types else "")
    all_cloud_images = data['all_cloud_images']
    active_cloud_image = data['active_cloud_image'] or (all_cloud_images[0] if all_cloud_images else "")

    root.title("Three-Tab UI")
    root.wm_attributes("-topmost", 1)  # optional

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # ---------------- Tab 1: "Actions" ----------------
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text=" Actions ")

    frame_models1 = tk.Frame(tab1)
    frame_models1.pack(padx=10, pady=5)
    tk.Label(frame_models1, text="Model:").pack(side="left")

    var_cloud_type_tab1 = tk.StringVar(value=active_cloud_type)
    dropdown_cloud_type_tab1 = ttk.Combobox(
        frame_models1, 
        textvariable=var_cloud_type_tab1, 
        values=all_cloud_types,
        state="readonly",
        justify="left",
        width=30
    )
    dropdown_cloud_type_tab1.pack(padx=10, pady=5)

    frame_actions = tk.Frame(tab1)
    frame_actions.pack(padx=10, pady=5)
    tk.Label(frame_actions, text="Action:").pack(side="left")

    var_action_tab1 = tk.StringVar(value="Refine")
    dropdown_action_tab1 = ttk.Combobox(
        frame_actions, 
        textvariable=var_action_tab1, 
        values=list(ACTION_MAP.keys()),
        state="readonly",
        justify="left",
        width=30
    )
    dropdown_action_tab1.pack(padx=10, pady=5)

    def submit_tab1():
        selected_cloud_type = var_cloud_type_tab1.get()
        selected_action_key = var_action_tab1.get()
        call_process(selected_cloud_type, ACTION_MAP[selected_action_key], '')

    btn_tab1 = tk.Button(tab1, text="Execute", command=submit_tab1, default="normal")
    btn_tab1.pack(padx=10, pady=10)

    # Label + read-only output box
    tk.Label(tab1, text="Output:").pack(anchor="w", padx=10)
    tab1_output = tk.Text(tab1, font=("TkDefaultFont", 9), height=6, width=60, state='disabled')
    tab1_output.pack(padx=10, pady=5)

    # ---------------- Tab 2: "Images" ----------------
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text=" Image Generation ")

    frame_models2 = tk.Frame(tab2)
    frame_models2.pack(padx=10, pady=5)
    tk.Label(frame_models2, text="Model:").pack(side="left")

    var_cloud_img_tab2 = tk.StringVar(value=active_cloud_image)
    dropdown_cloud_img_tab2 = ttk.Combobox(
        frame_models2, 
        textvariable=var_cloud_img_tab2, 
        values=all_cloud_images,
        state="readonly",
        justify="left",
        width=30
    )
    dropdown_cloud_img_tab2.pack(padx=10, pady=5)

    def submit_tab2():
        selected_image_model = var_cloud_img_tab2.get()
        call_process(selected_image_model, "image", '')

    btn_tab2 = tk.Button(tab2, text="1 Image", command=submit_tab2, default='normal')
    btn_tab2.pack(padx=10, pady=5)

    def submit_tab2_5():
        selected_image_model = var_cloud_img_tab2.get()
        call_process(selected_image_model, "image_5", '')

    btn_tab2_5 = tk.Button(tab2, text="5 Images", command=submit_tab2_5, default='normal')
    btn_tab2_5.pack(padx=10, pady=5)

    tk.Label(tab2, text="Output:").pack(anchor="w", padx=10)
    tab2_output = tk.Text(tab2, font=("TkDefaultFont", 9), height=6, width=60, state='disabled')
    tab2_output.pack(padx=10, pady=5)

    # ---------------- Tab 3: "LLM Freetext" ----------------
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text=" LLM Freetext ")

    frame_models3 = tk.Frame(tab3)
    frame_models3.pack(padx=10, pady=5)
    tk.Label(frame_models3, text="Model:").pack(side="left")

    var_cloud_type_tab3 = tk.StringVar(value=active_cloud_type)
    dropdown_cloud_type_tab3 = ttk.Combobox(
        frame_models3, 
        textvariable=var_cloud_type_tab3, 
        values=all_cloud_types,
        state="readonly",
        justify="left",
        width=30
    )
    dropdown_cloud_type_tab3.pack(padx=10, pady=5)

    tk.Label(tab3, text="Input:").pack(anchor="w", padx=10)
    txt_llm_tab3 = tk.Text(tab3, height=4, width=51)
    txt_llm_tab3.pack(padx=10, pady=5)

    def submit_tab3():
        selected_cloud_type = var_cloud_type_tab3.get()
        user_text = txt_llm_tab3.get("1.0", tk.END).strip()
        if user_text == "":
            return
        call_process(selected_cloud_type, 'freetext', user_text)

    btn_tab3 = tk.Button(tab3, text="Execute", command=submit_tab3)
    btn_tab3.pack(padx=10, pady=10)

    tk.Label(tab3, text="Output:").pack(anchor="w", padx=10)
    tab3_output = tk.Text(tab3, font=("TkDefaultFont", 9), height=6, width=60, state='disabled')
    tab3_output.pack(padx=10, pady=5)

    # Mapping tab labels to text widgets
    tab_to_textbox = {
        " Actions ": tab1_output,
        " Image Generation ": tab2_output,
        " LLM Freetext ": tab3_output
    }

    def on_tab_changed(event):
        current_tab = event.widget.tab('current')['text']
        sys.stdout = TextRedirector(tab_to_textbox[current_tab])
        if current_tab == " Actions ":
            btn_tab1.focus_set()
        elif current_tab == " Image Generation ":
            btn_tab2.focus_set()
        elif current_tab == " LLM Freetext ":
            btn_tab3.focus_set()

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
    sys.stdout = TextRedirector(tab1_output)

    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    main_ui()
