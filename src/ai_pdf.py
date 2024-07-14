import os
import sys
import pymupdf4llm
import pathlib

def load_pdf_files():
    md_texts = {}
    input_folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "input")

    if os.path.exists(input_folder_path):

        for root, dirs, files in os.walk(input_folder_path):  
            for filename in files:  
                if filename.endswith('.pdf'):  
                    input_file_path = os.path.join(root, filename)
                    output_file_path = input_file_path.lower().replace(".pdf", ".md")

                    if not os.path.exists(output_file_path):
                        md_text = pymupdf4llm.to_markdown(input_file_path)
                        pathlib.Path(output_file_path).write_bytes(md_text.encode())
                    
                    with open(output_file_path, 'r') as file:
                        md_texts[filename] = file.read()

    return md_texts
