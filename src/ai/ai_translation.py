import config_translate as cfg
from types import SimpleNamespace
import requests
import json

def call_translation_ai(text, language):

    config = cfg.get_translation_config()

    if config.CLOUD_TYPE_TRANSLATION != "":

        # DeepL
        if "DEEPL" in config.CLOUD_TYPE_TRANSLATION:
    
            payload = {
                "text": [ 
                    text
                ],
                "target_lang": language,
                "preserve_formatting": True,
                #"formality": "more" # only supported for source language EN?
            }

            response = requests.post(
                config.DEEPL_BASE_URL,
                headers=config.TRANSLATION_HEADERS,
                data=json.dumps(payload)
            )
            response_text = response.text
            response_status = response.status_code

            if response_status != 200:
                raise Exception(f"Error: {response_status} - {response_text}")

            parsed_json = json.loads(response_text)
            result = parsed_json['translations'][0]['text']

        return result
