import gradio as gr
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

# Placeholder for the external function call
def process_action(user_choice):
    real_action = ACTION_MAP[user_choice]
    charttype = "auto"
    process.main(real_action, charttype)
    return f"Executed action: {real_action}"

def launch_app():
    with gr.Blocks() as demo:
        action_dropdown = gr.Dropdown(
            label="Choose an action",
            choices=list(ACTION_MAP.keys()),
            value="Refine"
        )

        output_box = gr.Textbox(
            label="Result",
            lines=2
        )

        submit_button = gr.Button("Submit")

        submit_button.click(
            fn=process_action,
            inputs=action_dropdown,
            outputs=output_box
        )

    demo.launch()

if __name__ == "__main__":
    launch_app()
