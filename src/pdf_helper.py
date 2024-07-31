import os
import sys
import pymupdf4llm
import pathlib
import text_helper
import tiktoken

def load_pdf_files(optimization_level=2):
    md_texts = {}
    input_folder_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "input")
    if os.path.exists(input_folder_path):
        for root, dirs, files in os.walk(input_folder_path):  
            for filename in files:  
                if filename.endswith('.pdf'):  
                    input_file_path = os.path.join(root, filename)
                    output_file_path = input_file_path.lower().replace(".pdf", ".md")

                    if not os.path.exists(output_file_path):
                        md_text = pymupdf4llm.to_markdown(input_file_path) #, page_chunks=True)
                        token_count = text_helper.num_tokens_from_string(md_text, "cl100k_base")
                        if optimization_level > 0:
                            pathlib.Path(output_file_path.replace(".md", "_original.md")).write_bytes(md_text.encode())

                            if optimization_level > 0:
                                md_text = text_helper.remove_section(md_text, "Introduction")
                                md_text = text_helper.remove_section(md_text, "Conclusion")
                                md_text = text_helper.remove_section(md_text, "References")
                            
                            if optimization_level > 1:
                                if optimization_level > 2:
                                    md_text = text_helper.ultra_minimize_tokens(md_text)
                                else:
                                    md_text = text_helper.cleanse_markdown(md_text)

                            pathlib.Path(output_file_path).write_bytes(md_text.encode())

                            token_count_cleaned = text_helper.num_tokens_from_string(md_text, "cl100k_base")
                            print(f"Token count: {token_count} -> {token_count_cleaned} @ level {optimization_level}")
                        else:
                            pathlib.Path(output_file_path).write_bytes(md_text.encode())
                    
                    with open(output_file_path, 'r') as file:
                        md_texts[filename] = file.read()
    return md_texts
