import os
import sys
import pymupdf4llm
import pymupdf
import pathlib
import text_helper
import base64
from math import ceil
from PIL import Image
import io

def load_pdf_files(optimization_level=2, as_images=False, as_images_dpi=200, mime_type="image/png", as_base64=False):
    docs = {}
    input_folder_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "input"), "pdf")
    if os.path.exists(input_folder_path):
        for root, dirs, files in os.walk(input_folder_path):  
            for filename in files:  
                if filename.endswith('.pdf'):  
                    input_file_path = os.path.join(root, filename)

                    if not as_images:
                        output_file_path = input_file_path.lower().replace(".pdf", ".md")
                        if not os.path.exists(output_file_path):
                            doc = pymupdf4llm.to_markdown(input_file_path) #, page_chunks=True)
                            extract_and_optimize(optimization_level, output_file_path, doc)
                        if as_base64:
                            docs[filename] = load_file_as_base64(output_file_path)
                        else:                    
                            with open(output_file_path, 'r') as file:
                                docs[filename] = file.read()
                    else:
                        images = []
                        for page in pymupdf.open(input_file_path):
                            pix = page.get_pixmap(dpi=as_images_dpi)
                            output_file_path = input_file_path.lower().replace(".pdf", ("-page-%i.png" % page.number))
                            if not os.path.exists(output_file_path):
                                pix.save(output_file_path)
                            if as_base64:
                                images.append(load_file_as_base64(output_file_path))
                            else:                    
                                with open(output_file_path, 'rb') as file:
                                    images.append(file.read())
                        docs[filename] = images
    return docs

def extract_and_optimize(optimization_level, output_file_path, md_text):
    token_count = text_helper.num_tokens_from_string(md_text, "cl100k_base")
    if optimization_level > 0:
        pathlib.Path(output_file_path.replace(".md", "_original.md")).write_bytes(md_text.encode())

        if optimization_level > 0:
            md_text = text_helper.remove_section(md_text, "Introduction")
            md_text = text_helper.remove_section(md_text, "Conclusion")
            md_text = text_helper.remove_section(md_text, "References")
                            
        if optimization_level > 1:
            md_text = text_helper.cleanse_markdown(md_text, optimization_level)

        pathlib.Path(output_file_path).write_bytes(md_text.encode())

        token_count_cleaned = text_helper.num_tokens_from_string(md_text, "cl100k_base")
        print(f"Token count: {token_count} -> {token_count_cleaned} @ level {optimization_level}")
    else:
        pathlib.Path(output_file_path).write_bytes(md_text.encode())

def load_pdfsimple_files():
    docs_base64 = {}
    input_folder_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "input"), "pdf")
    if os.path.exists(input_folder_path):
        for root, dirs, files in os.walk(input_folder_path):  
            for filename in files:  
                if filename.endswith('.pdf'):  
                    input_file_path = os.path.join(root, filename)
                    docs_base64[filename] = load_file_as_base64(input_file_path)
    return docs_base64

def load_file_as_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            binary_data = file.read()
            base64_encoded = base64.b64encode(binary_data)
            base64_string = base64_encoded.decode('utf-8')                        
            return base64_string

def load_text_files(format="md"):
    md_texts = {}
    input_folder_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "input"), format)
    if os.path.exists(input_folder_path):
        for root, dirs, files in os.walk(input_folder_path):  
            for filename in files:  
                if filename.endswith("." + format):  
                    input_file_path = os.path.join(root, filename)
                    with open(input_file_path, 'r') as file:
                        md_texts[filename] = file.read()
    return md_texts

def calculate_image_tokens(base64_image: str) -> int:
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    width, height = image.size

    if width > 2048 or height > 2048:
        aspect_ratio = width / height
        if aspect_ratio > 1:
            width, height = 2048, int(2048 / aspect_ratio)
        else:
            width, height = int(2048 * aspect_ratio), 2048

    if width >= height and height > 768:
        width, height = int((768 / height) * width), 768
    elif height > width and width > 768:
        width, height = 768, int((768 / width) * height)

    tiles_width = ceil(width / 512)
    tiles_height = ceil(height / 512)

    total_tokens = 85 + 170 * (tiles_width * tiles_height)
    return total_tokens
