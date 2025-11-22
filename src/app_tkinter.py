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
    "Refine (Grounding)": "refine_grounding",
    "Refine (Dev)": "refine_dev",
    "Examples": "examples",
    "Cluster": "cluster",
    "Glossary (md/html)": "glossary",
    "Argumentation (md/html)": "argumentation",
    "Export markmap (md/html)": "export_markmap",
    "Export mermaid (md/html)": "export_mermaid",
    "Pdf to mindmap": "pdf_mindmap",
    "Pdf to mindmap (via knowledge graph)": "pdf_knowledgegraph",
    "Pdf simple (by image)": "pdfsimple_mindmap",
    "Import MD": "import_md"
}

def load_image_prompts():
    directory_path = os.path.join(os.path.dirname(__file__), 'ai', 'image_prompts')
    try:
        file_names = os.listdir(directory_path)
        file_dict = {
            file.replace(".py", "").replace("_", " ").title(): \
                file for file in file_names \
                    if os.path.isfile(os.path.join(directory_path, file)) and file.endswith(".py") and not file.startswith("_")
        }
        return file_dict
    except FileNotFoundError:
        return {}



def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_agents():
    directory_path = os.path.join(os.path.dirname(__file__), 'ai', 'agents')
    try:
        file_names = os.listdir(directory_path)
        file_dict = {
            file.replace(".py", "").replace("_", " ").title(): \
                file for file in file_names \
                    if os.path.isfile(os.path.join(directory_path, file)) and file.endswith(".py") and not file.startswith("_")
        }
        return file_dict
    except FileNotFoundError:
        return {}


def parse_cloud_definitions(filename_llm, filename_image):
    """
    Reads config.py lines to find
       CLOUD_TYPE = '...' 
       CLOUD_TYPE_IMAGE = '...'
    and returns all + currently active.
    """
    cloud_type_pattern = re.compile(r"CLOUD_TYPE\s*=\s*'([^']*)'")
    cloud_type_img_pattern = re.compile(r"CLOUD_TYPE_IMAGE\s*=\s*'([^']*)'")

    cloud_types = []
    uncommented_cloud_type = None
    cloud_images = []
    uncommented_cloud_image = None
    
    with open(filename_llm, 'r', encoding='utf-8') as f:
        for line in f:
            match_type = cloud_type_pattern.search(line)
            if match_type:
                value = match_type.group(1).strip()
                if value:
                    cloud_types.append(value)
                    if not line.lstrip().startswith('#'):
                        uncommented_cloud_type = value
            
    with open(filename_image, 'r', encoding='utf-8') as f:
        for line in f:
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


class MindmanagerAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mindmanager AI")
        self.wm_attributes("-topmost", 1)  # optional "always on top"

        # Prepare data & settings
        self.settings_data = load_settings()
        
        config_file_llm = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config_llm.py'))
        config_file_image = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config_image.py'))
        data = parse_cloud_definitions(config_file_llm, config_file_image)
        agents = load_agents()

        self.all_cloud_types = data['all_cloud_types']
        self.active_cloud_type = data['active_cloud_type'] or (
            self.all_cloud_types[0] if self.all_cloud_types else ""
        )
        self.all_cloud_images = data['all_cloud_images']
        self.active_cloud_image = data['active_cloud_image'] or (
            self.all_cloud_images[0] if self.all_cloud_images else ""
        )

        # Load or init stored values:
        self.agentic_model_strong = self.settings_data.get("agentic_model_strong", self.active_cloud_type)
        self.agentic_model_cheap = self.settings_data.get("agentic_model_cheap", self.active_cloud_type)
        self.chartType = self.settings_data.get("chartType", "auto")
        self.modifyLiveMap = self.settings_data.get("modifyLiveMap", False)

        # Create Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Keep references to text widgets so we can redirect stdout
        self.tab_to_textbox = {}
        
        # Create all tabs
        self.create_tab_actions()      # Tab 1: "Actions"
        self.create_tab_images()       # Tab 2: "Image Generation"
        self.create_tab_freetext()     # Tab 3: "LLM Freetext"
        self.create_tab_translation()  # Tab 4: "Translation"
        self.create_tab_agentic()      # Tab 5: "Agentic"
        self.create_tab_settings()     # Tab 6: "Settings"

        # Bind event to switch stdout redirection to correct tab
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Redirect stdout to first tab initially
        first_tab_text = next(iter(self.tab_to_textbox.values()), None)
        if first_tab_text:
            sys.stdout = TextRedirector(first_tab_text)

        # Final geometry handling
        self.geometry("375x330")
        self.update_idletasks()  
        actual_width = self.winfo_width()
        actual_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        x = screen_width - actual_width  # place at right edge
        y = 75                            # place at top
        self.geometry(f"+{x}+{y}")

        sv_ttk.set_theme("dark")

    def on_tab_changed(self, event):
        current_tab = event.widget.tab('current')['text']
        if self.tab_to_textbox.get(current_tab):
            sys.stdout = TextRedirector(self.tab_to_textbox[current_tab])
        else:
            # revert to console or do something else
            sys.stdout = sys.__stdout__

        # Optional focusing on a default button in each tab
        if current_tab == "Actn" and hasattr(self, "btn_tab1"):
            self.btn_tab1.focus_set()
        elif current_tab == "Img" and hasattr(self, "btn_tab2_1"):
            self.btn_tab2_1.focus_set()
        elif current_tab == "Txt" and hasattr(self, "btn_tab3"):
            self.btn_tab3.focus_set()
        elif current_tab == "Trnsl" and hasattr(self, "btn_tab4"):
            self.btn_tab4.focus_set()
        elif current_tab == "Agnt" and hasattr(self, "btn_tab5"):
            self.btn_tab5.focus_set()
    
    # ------------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------------
    def build_payload(self, model, action, data=None):
        """Build a standard payload dict."""
        if data is None:
            data = {}
        return {
            "model": model,
            "action": action,
            "data": data,
            "settings": {
                "chartType": self.chartType,
                "modifyLiveMap": self.modifyLiveMap
            }
        }

    def call_process_json(self, payload_dict):
        print("Process called. Please wait...")
        self.update()
        self.update_idletasks()
        process.ui_main(payload_dict)

    def create_output_box(self, parent, tab_name):
        """Create a label 'Output:' + text box, store in tab_to_textbox."""
        ttk.Label(parent, text="Output:").pack(anchor="w", padx=10)
        txt = tk.Text(
            parent, font=("TkDefaultFont", 9),
            state='disabled', highlightbackground="gray"
        )
        txt.pack(padx=10, pady=5, fill="both", expand=True)
        self.tab_to_textbox[tab_name] = txt
        return txt

    def create_labeled_combobox(self, parent, label_text, var, values, width=34, label_width=7):
        """Create a label + Combobox row with aligned columns."""
        frame = ttk.Frame(parent)
        frame.pack(padx=10, pady=5, fill="x")
        ttk.Label(frame, text=label_text, width=label_width, anchor="w").grid(row=0, column=0, sticky="w")
        combo = ttk.Combobox(
            frame, textvariable=var, values=values,
            state="readonly", justify="left", width=width
        )
        combo.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        frame.grid_columnconfigure(1, weight=1)
        return combo

    # ------------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------------
    def create_tab_actions(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Actn")

        # Model combobox
        self.var_cloud_type_tab1 = tk.StringVar(value=self.active_cloud_type)
        self.create_labeled_combobox(
            tab, "Model:", self.var_cloud_type_tab1, self.all_cloud_types
        )

        # Action combobox
        self.var_action_tab1 = tk.StringVar(value="Refine")
        self.create_labeled_combobox(
            tab, "Action:", self.var_action_tab1, list(ACTION_MAP.keys())
        )

        def submit_tab1():
            selected_cloud_type = self.var_cloud_type_tab1.get()
            selected_action_key = self.var_action_tab1.get()
            action_val = ACTION_MAP[selected_action_key]
            payload = self.build_payload(selected_cloud_type, action_val)
            self.call_process_json(payload)

        # Execute button
        self.btn_tab1 = ttk.Button(tab, text="Execute", command=submit_tab1, default="normal")
        self.btn_tab1.pack(padx=10, pady=10)

        # Output
        self.create_output_box(tab, "Actn")

    def create_tab_images(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Img")

        # Model combobox
        self.var_cloud_img_tab2 = tk.StringVar(value=self.active_cloud_image)
        self.create_labeled_combobox(
            tab, "Model:", self.var_cloud_img_tab2, self.all_cloud_images
        )

        image_prompts = load_image_prompts()
        image_prompt_names = sorted(image_prompts.keys())
        default_prompt = "Generic" if "Generic" in image_prompt_names else (image_prompt_names[0] if image_prompt_names else "")
        self.var_image_action_tab2 = tk.StringVar(value=default_prompt)
        self.create_labeled_combobox(
            tab, "Type:", self.var_image_action_tab2, image_prompt_names
        )

        def submit_tab2():
            selected_image_model = self.var_cloud_img_tab2.get()
            selected_action_key = self.var_image_action_tab2.get()
            prompt_file = image_prompts.get(selected_action_key, "")
            prompt_base = os.path.splitext(prompt_file)[0] if prompt_file else "generic"
            action = "image" if prompt_base == "generic" else f"image_{prompt_base}"
            payload = self.build_payload(selected_image_model, action)
            self.call_process_json(payload)

        # Buttons
        self.btn_tab2_1 = ttk.Button(tab, text="Generate",
                                     command=submit_tab2, default='normal')
        self.btn_tab2_1.pack(padx=10, pady=10)

        # Output
        self.create_output_box(tab, "Img")

    def create_tab_freetext(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Txt")

        # Model combobox
        self.var_cloud_type_tab3 = tk.StringVar(value=self.active_cloud_type)
        self.create_labeled_combobox(
            tab, "Model:", self.var_cloud_type_tab3, self.all_cloud_types
        )

        # Input text
        ttk.Label(tab, text="LLM prompt for content:").pack(anchor="w", padx=10)
        self.txt_llm_tab3 = tk.Text(tab, height=4, width=54, highlightbackground="gray")
        self.txt_llm_tab3.pack(padx=10, pady=5, fill="x", expand=True)

        def submit_tab3():
            selected_cloud_type = self.var_cloud_type_tab3.get()
            user_text = self.txt_llm_tab3.get("1.0", tk.END).strip()
            if not user_text:
                return
            data = {"freetext": user_text}
            payload = self.build_payload(selected_cloud_type, "freetext", data)
            self.call_process_json(payload)

        self.btn_tab3 = ttk.Button(tab, text="Execute", command=submit_tab3)
        self.btn_tab3.pack(padx=10, pady=10)

        # Output
        self.create_output_box(tab, "Txt")

    def create_tab_translation(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Trnsl")

        # Model combobox
        self.var_translation_model = tk.StringVar(value="DEEPL")
        self.create_labeled_combobox(tab, "Model:", self.var_translation_model, ["DEEPL"], width=20)

        # Source combobox
        frame_lang_source = ttk.Frame(tab)
        frame_lang_source.pack(padx=10, pady=5)
        ttk.Label(frame_lang_source, text="Source:").pack(side="left")
        self.var_translation_source = tk.StringVar(value="auto")
        dropdown_translation_source = ttk.Combobox(
            frame_lang_source,
            textvariable=self.var_translation_source,
            values=["auto"],
            state="readonly",
            justify="left",
            width=20
        )
        dropdown_translation_source.pack(side="left", padx=5)

        # Target combobox
        frame_lang_target = ttk.Frame(tab)
        frame_lang_target.pack(padx=10, pady=5)
        ttk.Label(frame_lang_target, text="Target:").pack(side="left")
        self.var_translation_target = tk.StringVar(value="DE")
        dropdown_translation_target = ttk.Combobox(
            frame_lang_target,
            textvariable=self.var_translation_target,
            values=[
                "EN-US", "EN-GB", "DE", "BG", "CS", "DA", "EL", "ES", "ET", "FI", "FR", 
                "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT-BR", 
                "PT-PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH"
            ],
            state="readonly",
            justify="left",
            width=20
        )
        dropdown_translation_target.pack(side="left", padx=5)

        def submit_tab4():
            mdl = self.var_translation_model.get()
            tgt = self.var_translation_target.get()
            action_val = f"translate_{mdl.lower()}+{tgt}"
            payload = self.build_payload(mdl, action_val)
            self.call_process_json(payload)

        self.btn_tab4 = ttk.Button(tab, text="Execute", command=submit_tab4)
        self.btn_tab4.pack(padx=10, pady=10)

        # Output
        self.create_output_box(tab, "Trnsl")

    def create_tab_agentic(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Agnt")

        # Action combobox
        frame_action5 = ttk.Frame(tab)
        frame_action5.pack(padx=10, pady=5)
        ttk.Label(frame_action5, text="Action:").pack(side="left")
        agent_actions = sorted(load_agents().keys())
        self.var_agentic_action = tk.StringVar(value=agent_actions[0] if agent_actions else "")
        dropdown_agentic_action = ttk.Combobox(
            frame_action5,
            textvariable=self.var_agentic_action,
            values=sorted(load_agents().keys()),
            state="readonly",
            justify="left",
            width=34
        )
        dropdown_agentic_action.pack(side="left", padx=5)

        ### Model comboboxes ###
        filtered_cloud_types = [x for x in self.all_cloud_types if x.lower().startswith(('openai', 'azure', 'ollama', 'xai', 'deepseek'))]
    
        # Strong model combobox
        self.var_agentic_strong = tk.StringVar(value=self.agentic_model_strong)
        self.create_labeled_combobox(
            tab, "Strong:", self.var_agentic_strong, filtered_cloud_types
        )

        # Cheap model combobox
        self.var_agentic_cheap = tk.StringVar(value=self.agentic_model_cheap)
        self.create_labeled_combobox(
            tab, "Cheap:", self.var_agentic_cheap, filtered_cloud_types
        )

        def submit_tab5():
            model_strong = self.var_agentic_strong.get()
            model_cheap = self.var_agentic_cheap.get()
            action_val = self.var_agentic_action.get()
            # Persist these so they initialize on next start
            self.settings_data["agentic_model_strong"] = model_strong
            self.settings_data["agentic_model_cheap"] = model_cheap
            save_settings(self.settings_data)

            agent_action = load_agents().get(action_val)
            data = {
                "agent_action": agent_action,
                "model_strong": model_strong,
                "model_cheap": model_cheap
            }
            payload = self.build_payload(model_strong, "agent", data)
            self.call_process_json(payload)

        self.btn_tab5 = ttk.Button(tab, text="Execute", state="normal", command=submit_tab5)
        self.btn_tab5.pack(padx=10, pady=10)

        # Output
        self.create_output_box(tab, "Agnt")

    def create_tab_settings(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Conf")

        # chartType
        frame_chart = ttk.Frame(tab)
        frame_chart.pack(padx=10, pady=5)
        ttk.Label(frame_chart, text="ChartType:").pack(side="left")
        self.var_chartType = tk.StringVar(value=self.chartType)
        dropdown_chartType = ttk.Combobox(
            frame_chart,
            textvariable=self.var_chartType,
            values=["auto", "radial", "orgchart"],
            state="readonly", justify="left", width=13
        )
        dropdown_chartType.pack(side="left", padx=5)

        # liveMap
        frame_liveMap = ttk.Frame(tab)
        frame_liveMap.pack(padx=10, pady=5)
        self.var_liveMap = tk.BooleanVar(value=self.modifyLiveMap)
        chk_liveMap = ttk.Checkbutton(
            frame_liveMap, 
            text="Modify live map, dont create new", 
            variable=self.var_liveMap, 
            state="disabled"
        )
        chk_liveMap.pack(side="left")

        def save_settings_tab6():
            self.settings_data["chartType"] = self.var_chartType.get()
            self.settings_data["modifyLiveMap"] = self.var_liveMap.get()
            save_settings(self.settings_data)
            print("Settings saved.")

        btn_save_settings = ttk.Button(tab, text="Save", command=save_settings_tab6)
        btn_save_settings.pack(padx=10, pady=10)

        # Output
        self.create_output_box(tab, "Conf")


def main():
    app = MindmanagerAIApp()
    app.mainloop()


if __name__ == "__main__":
    main()
