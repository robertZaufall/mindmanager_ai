import tkinter as tk
from tkinter import ttk
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

def process_action():
    real_action = ACTION_MAP[action_var.get()]
    charttype = "auto"
    process.main(real_action, charttype)  # call your external function
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Executed action: {real_action}")

root = tk.Tk()
root.title("Mindmanager AI")

# Keep the window always on top
root.wm_attributes("-topmost", 1)

action_var = tk.StringVar(value="Refine")
dropdown = ttk.Combobox(root, textvariable=action_var, values=list(ACTION_MAP.keys()))
dropdown.pack(padx=10, pady=5)

submit_button = tk.Button(root, text="Submit", command=process_action)
submit_button.pack(padx=10, pady=5)

output_text = tk.Text(root, height=2, width=40)
output_text.pack(padx=10, pady=5)

root.mainloop()
