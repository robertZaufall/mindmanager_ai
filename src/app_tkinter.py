import tkinter as tk
from tkinter import ttk
import sv_ttk

import process
import re
import os
import sys
import json

SETTINGS_FILE = "settings.json"

ACTION_MAP = {
    "Refine": "refine",
    "Refine (Dev)": "refine_dev",
    "Examples": "examples",
    "Cluster": "cluster",
    "Glossary": "glossary",
    "Argumentation": "argumentation",
    "Image": "image",
    "Export markmap": "export_markmap",
    "Export mermaid": "export_mermaid",
    "Pdf to mindmap": "pdf_mindmap",
    "Pdf to mindmap (via knowledge graph)": "pdf_knowledgegraph",
    "Pdf simple (by image)": "pdfsimple_mindmap",
    "Import MD": "import_md"
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def parse_cloud_definitions(filename):
    """
    Reads config.py lines to find
       CLOUD_TYPE = '...' 
       CLOUD_TYPE_IMAGE = '...'
    and returns all + currently active.
    """
    import re
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

    #cloud_types = [ct for ct in cloud_types if "DEEPL" not in ct]

    return {
        'all_cloud_types': cloud_types,
        'active_cloud_type': uncommented_cloud_type,
        'all_cloud_images': cloud_images,
        'active_cloud_image': uncommented_cloud_image
    }


class TextRedirector:
    """
    Redirects stdout to a text widget so that
    print() statements go into the GUI instead of console.
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.config(state='normal')
        self.text_widget.insert('end', string)
        self.text_widget.see('end')
        self.text_widget.config(state='disabled')

    def flush(self):
        pass


def call_process_json(payload_dict):
    print(f"Process called. Please wait...")
    root.update()
    root.update_idletasks()
    process.ui_main(payload_dict)


def main_ui():
    global root, settings_data

    # Load or init settings (chartType, modifyLiveMap, agentic defaults, etc.)
    settings_data = load_settings()

    filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.py'))
    data = parse_cloud_definitions(filename)

    all_cloud_types = data['all_cloud_types']
    active_cloud_type = data['active_cloud_type'] or (all_cloud_types[0] if all_cloud_types else "")
    all_cloud_images = data['all_cloud_images']
    active_cloud_image = data['active_cloud_image'] or (all_cloud_images[0] if all_cloud_images else "")

    # Read or initialize stored values:
    agentic_model_strong = settings_data.get("agentic_model_strong", active_cloud_type)
    agentic_model_cheap = settings_data.get("agentic_model_cheap", active_cloud_type)
    chartType = settings_data.get("chartType", "auto")
    modifyLiveMap = settings_data.get("modifyLiveMap", False)

    root.title("Mindmanager AI")
    root.wm_attributes("-topmost", 1)  # optional

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # ----------------------------------------------------------------------------------
    # Tab 1: "Actions"
    # ----------------------------------------------------------------------------------
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Actn")

    frame_models1 = ttk.Frame(tab1)
    frame_models1.pack(padx=10, pady=5)
    ttk.Label(frame_models1, text="Model:").pack(side="left")

    var_cloud_type_tab1 = tk.StringVar(value=active_cloud_type)
    dropdown_cloud_type_tab1 = ttk.Combobox(
        frame_models1, 
        textvariable=var_cloud_type_tab1, 
        values=all_cloud_types,
        state="readonly", 
        justify="left",
        width=34
    )
    dropdown_cloud_type_tab1.pack(padx=10, pady=5)

    frame_actions = ttk.Frame(tab1)
    frame_actions.pack(padx=10, pady=5)
    ttk.Label(frame_actions, text="Action:").pack(side="left")

    var_action_tab1 = tk.StringVar(value="Refine")
    dropdown_action_tab1 = ttk.Combobox(
        frame_actions, 
        textvariable=var_action_tab1, 
        values=list(ACTION_MAP.keys()),
        state="readonly", 
        justify="left",
        width=34
    )
    dropdown_action_tab1.pack(padx=10, pady=5)

    def submit_tab1():
        selected_cloud_type = var_cloud_type_tab1.get()
        selected_action_key = var_action_tab1.get()
        payload = {
            "model": selected_cloud_type,
            "action": ACTION_MAP[selected_action_key],
            "data": {},
            "settings": {
                "chartType": var_chartType.get(),
                "modifyLiveMap": modifyLiveMap
            }
        }
        call_process_json(payload)

    btn_tab1 = ttk.Button(tab1, text="Execute", command=submit_tab1, default="normal")
    btn_tab1.pack(padx=10, pady=10)

    ttk.Label(tab1, text="Output:").pack(anchor="w", padx=10)
    tab1_output = tk.Text(tab1, font=("TkDefaultFont", 9), state='disabled', highlightbackground="gray")
    tab1_output.pack(padx=10, pady=5, fill="both", expand=True)

    # ----------------------------------------------------------------------------------
    # Tab 2: "Image Generation"
    # ----------------------------------------------------------------------------------
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text="Img")

    frame_models2 = ttk.Frame(tab2)
    frame_models2.pack(padx=10, pady=5)
    ttk.Label(frame_models2, text="Model:").pack(side="left")

    var_cloud_img_tab2 = tk.StringVar(value=active_cloud_image)
    dropdown_cloud_img_tab2 = ttk.Combobox(
        frame_models2,
        textvariable=var_cloud_img_tab2,
        values=all_cloud_images,
        state="readonly",
        justify="left",
        width=34
    )
    dropdown_cloud_img_tab2.pack(padx=10, pady=5)

    def submit_tab2(action):
        selected_image_model = var_cloud_img_tab2.get()
        payload = {
            "model": selected_image_model,
            "action": action,
            "data": {},
            "settings": {
                "chartType": var_chartType.get(),
                "modifyLiveMap": modifyLiveMap
            }
        }
        call_process_json(payload)

    btn_tab2_1 = ttk.Button(tab2, text="1 Image", command=lambda: submit_tab2("image"), default='normal')
    btn_tab2_1.pack(side="top", padx=10, pady=5)

    button_frame_image = ttk.Frame(tab2)
    button_frame_image.pack(side="top", padx=10, pady=5)

    btn_tab2_5 = ttk.Button(button_frame_image, text="5 Images", command=lambda: submit_tab2("image_5"), default='normal')
    btn_tab2_5.pack(side="left", padx=10, pady=5)

    btn_tab2_10 = ttk.Button(button_frame_image, text="10 Images", command=lambda: submit_tab2("image_10"), default='normal')
    btn_tab2_10.pack(side="left", padx=10, pady=5)

    button_frame_image.pack(anchor="center")

    ttk.Label(tab2, text="Output:").pack(anchor="w", padx=10)
    tab2_output = tk.Text(tab2, font=("TkDefaultFont", 9), state='disabled', highlightbackground="gray")
    tab2_output.pack(side="top", padx=10, pady=5, fill="both", expand=True)

    # ----------------------------------------------------------------------------------
    # Tab 3: "LLM Freetext"
    # ----------------------------------------------------------------------------------
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text="Txt")

    frame_models3 = ttk.Frame(tab3)
    frame_models3.pack(padx=10, pady=5)
    ttk.Label(frame_models3, text="Model:").pack(side="left")

    var_cloud_type_tab3 = tk.StringVar(value=active_cloud_type)
    dropdown_cloud_type_tab3 = ttk.Combobox(
        frame_models3,
        textvariable=var_cloud_type_tab3,
        values=all_cloud_types,
        state="readonly",
        justify="left",
        width=34
    )
    dropdown_cloud_type_tab3.pack(padx=10, pady=5)

    ttk.Label(tab3, text="Input:").pack(anchor="w", padx=10)
    txt_llm_tab3 = tk.Text(tab3, height=4, width=54, highlightbackground="gray")
    txt_llm_tab3.pack(padx=10, pady=5, fill="x", expand=True)

    def submit_tab3():
        selected_cloud_type = var_cloud_type_tab3.get()
        user_text = txt_llm_tab3.get("1.0", ttk.END).strip()
        if not user_text:
            return
        payload = {
            "model": selected_cloud_type,
            "action": "freetext",
            "data": {
                "freetext": user_text
            },
            "settings": {
                "chartType": var_chartType.get(),
                "modifyLiveMap": modifyLiveMap
            }
        }
        call_process_json(payload)

    btn_tab3 = ttk.Button(tab3, text="Execute", command=submit_tab3)
    btn_tab3.pack(padx=10, pady=10)

    ttk.Label(tab3, text="Output:").pack(anchor="w", padx=10)
    tab3_output = tk.Text(tab3, font=("TkDefaultFont", 9), state='disabled', highlightbackground="gray")
    tab3_output.pack(padx=10, pady=5, fill="x", expand=True)

    # ----------------------------------------------------------------------------------
    # Tab 4: "Translation"
    # ----------------------------------------------------------------------------------
    tab4 = ttk.Frame(notebook)
    notebook.add(tab4, text="Trnsl")

    frame_models4 = ttk.Frame(tab4)
    frame_models4.pack(padx=10, pady=5)
    ttk.Label(frame_models4, text="Model:").pack(side="left")

    var_translation_model = tk.StringVar(value="DEEPL")
    dropdown_translation_model = ttk.Combobox(
        frame_models4,
        textvariable=var_translation_model,
        values=["DEEPL"],
        state="readonly",
        justify="left",
        width=20
    )
    dropdown_translation_model.pack(side="left", padx=5)

    frame_lang_source = ttk.Frame(tab4)
    frame_lang_source.pack(padx=10, pady=5)
    ttk.Label(frame_lang_source, text="Source:").pack(side="left")
    var_translation_source = tk.StringVar(value="auto")
    dropdown_translation_source = ttk.Combobox(
        frame_lang_source,
        textvariable=var_translation_source,
        values=["auto"],
        state="readonly",
        justify="left",
        width=20
    )
    dropdown_translation_source.pack(side="left", padx=5)

    frame_lang_target = ttk.Frame(tab4)
    frame_lang_target.pack(padx=10, pady=5)
    ttk.Label(frame_lang_target, text="Target:").pack(side="left")
    var_translation_target = tk.StringVar(value="DE")
    dropdown_translation_target = ttk.Combobox(
        frame_lang_target,
        textvariable=var_translation_target,
        values=[
            "EN-US", "EN-GB", "DE", "BG", "CS", "DA", "EL", "ES", "ET", "FI", "FR", "HU", "ID", 
            "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT-BR", "PT-PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH"
        ],
        state="readonly",
        justify="left",
        width=20
    )
    dropdown_translation_target.pack(side="left", padx=5)

    def submit_tab4():
        #translate_deepl+EN-US, translate_deepl+DE
        mdl = var_translation_model.get()
        #src = var_translation_source.get() + "-" if var_translation_source.get() != "auto" else ""
        tgt = var_translation_target.get()
        payload = {
            "model": mdl,
            "action": f"translate_{mdl.lower()}+{tgt}",
            "data": {},
            "settings": {
                "chartType": var_chartType.get(),
                "modifyLiveMap": modifyLiveMap
            }
        }
        call_process_json(payload)

    btn_tab4 = ttk.Button(tab4, text="Execute", command=submit_tab4)
    btn_tab4.pack(padx=10, pady=10)

    ttk.Label(tab4, text="Output:").pack(anchor="w", padx=10)
    tab4_output = tk.Text(tab4, font=("TkDefaultFont", 9), state='disabled', highlightbackground="gray")
    tab4_output.pack(padx=10, pady=5, fill="both", expand=True)
    
    # ----------------------------------------------------------------------------------
    # Tab 5: "Agentic"
    # ----------------------------------------------------------------------------------
    tab5 = ttk.Frame(notebook)
    notebook.add(tab5, text="Agnt")

    frame_action5 = ttk.Frame(tab5)
    frame_action5.pack(padx=10, pady=5)
    ttk.Label(frame_action5, text="Action:").pack(side="left")
    var_agentic_action = tk.StringVar(value="Action 1")
    dropdown_agentic_action = ttk.Combobox(
        frame_action5,
        textvariable=var_agentic_action,
        values=["Action 1", "Action 2"],
        state="readonly",
        justify="left",
        width=34
    )
    dropdown_agentic_action.pack(side="left", padx=5)

    frame_models5 = ttk.Frame(tab5)
    frame_models5.pack(padx=10, pady=5)

    ttk.Label(frame_models5, text="Strong:").pack(side="left")
    var_agentic_strong = tk.StringVar(value=agentic_model_strong)
    dropdown_agentic_strong = ttk.Combobox(
        frame_models5,
        textvariable=var_agentic_strong,
        values=all_cloud_types,
        state="readonly",
        justify="left",
        width=34
    )
    dropdown_agentic_strong.pack(side="left", padx=5)

    frame_models6 = ttk.Frame(tab5)
    frame_models6.pack(padx=10, pady=5)

    ttk.Label(frame_models6, text="Cheap:").pack(side="left")
    var_agentic_cheap = tk.StringVar(value=agentic_model_cheap)
    dropdown_agentic_cheap = ttk.Combobox(
        frame_models6,
        textvariable=var_agentic_cheap,
        values=all_cloud_types,
        state="readonly",
        justify="left",
        width=34
    )
    dropdown_agentic_cheap.pack(side="left", padx=5)

    def submit_tab5():
        model_strong = var_agentic_strong.get()
        model_cheap = var_agentic_cheap.get()
        action_val = var_agentic_action.get()
        # Persist these so they initialize on next start
        settings_data["agentic_model_strong"] = model_strong
        settings_data["agentic_model_cheap"] = model_cheap
        save_settings(settings_data)

        payload = {
            "model": model_strong,
            "action": "agent",
            "data": {
                "agent_action": action_val,
                "model_strong": model_strong,
                "model_cheap": model_cheap
            },
            "settings": {
                "chartType": var_chartType.get(),
                "modifyLiveMap": modifyLiveMap
            }
        }
        call_process_json(payload)

    btn_tab5 = ttk.Button(tab5, text="Execute", state="normal", command=submit_tab5)
    btn_tab5.pack(padx=10, pady=10)

    ttk.Label(tab5, text="Output:").pack(anchor="w", padx=10)
    tab5_output = tk.Text(tab5, font=("TkDefaultFont", 9), state='disabled', highlightbackground="gray")
    tab5_output.pack(padx=10, pady=5, fill="both", expand=True)

    # ----------------------------------------------------------------------------------
    # Tab 6: "Settings"
    # ----------------------------------------------------------------------------------
    tab6 = ttk.Frame(notebook)
    notebook.add(tab6, text="Conf")

    frame_chart = ttk.Frame(tab6)
    frame_chart.pack(padx=10, pady=5)
    ttk.Label(frame_chart, text="ChartType:").pack(side="left")

    var_chartType = tk.StringVar(value=chartType)
    dropdown_chartType = ttk.Combobox(
        frame_chart,
        textvariable=var_chartType,
        values=["auto","radial","orgchart"],
        state="readonly",
        justify="left",
        width=13
    )
    dropdown_chartType.pack(side="left", padx=5)

    frame_liveMap = ttk.Frame(tab6)
    frame_liveMap.pack(padx=10, pady=5)
    var_liveMap = tk.BooleanVar(value=modifyLiveMap)
    chk_liveMap = ttk.Checkbutton(frame_liveMap, text="Modify live map, dont create new", variable=var_liveMap)
    chk_liveMap.pack(side="left")

    def save_settings_tab6():
        settings_data["chartType"] = var_chartType.get()
        settings_data["modifyLiveMap"] = var_liveMap.get()
        save_settings(settings_data)

    btn_save_settings = ttk.Button(tab6, text="Save", command=save_settings_tab6)
    btn_save_settings.pack(padx=10, pady=10)

    # ----------------------------------------------------------------------------------
    # Hook up outputs to a text box in first three tabs only
    # ----------------------------------------------------------------------------------
    tab_to_textbox = {
        "Actn": tab1_output,
        "Img": tab2_output,
        "Txt": tab3_output,
        "Trnsl": tab4_output,
        "Agnt": tab5_output,
        "Conf": None
    }

    def on_tab_changed(event):
        current_tab = event.widget.tab('current')['text']
        if tab_to_textbox.get(current_tab):
            sys.stdout = TextRedirector(tab_to_textbox[current_tab])
        else:
            # revert to console or do something else
            sys.stdout = sys.__stdout__
        # Optional focusing
        if current_tab == "Actn":
            btn_tab1.focus_set()
        elif current_tab == "Img":
            btn_tab2_1.focus_set()
        elif current_tab == "Txt":
            btn_tab3.focus_set()
        elif current_tab == "Trnsl":
            btn_tab4.focus_set()
        elif current_tab == "Agnt":
            btn_tab5.focus_set()

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    # Redirect stdout to first tab initially.
    sys.stdout = TextRedirector(tab1_output)

    root.geometry("375x330")

    root.update_idletasks()  # Let Tk finish calculating window geometry
    actual_width = root.winfo_width()
    actual_height = root.winfo_height()

    screen_width = root.winfo_screenwidth()
    x = screen_width - actual_width  # place at right edge
    y = 0                            # place at top

    root.geometry(f"+{x}+{y}")
    
    sv_ttk.set_theme("dark")
    root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    main_ui()
