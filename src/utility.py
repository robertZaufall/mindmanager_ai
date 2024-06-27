import re
import os

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
    folder_path = os.path.join(root_path, f"_{sanitize_folder_name(central_topic_text)}")
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    return folder_path