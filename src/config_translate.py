import os
from types import SimpleNamespace
from file_helper import load_env

CLOUD_TYPE_TRANSLATION = 'DEEPL'

def get_translation_config(CLOUD_TYPE_TRANSLATION: str = CLOUD_TYPE_TRANSLATION) -> SimpleNamespace:

    config = SimpleNamespace(
        CLOUD_TYPE_TRANSLATION=CLOUD_TYPE_TRANSLATION
    )

    config.LOG = True
    config.TURBO_MODE = True # just generate text topics

    load_env(CLOUD_TYPE_TRANSLATION.split("+")[0])

    if "DEEPL" in CLOUD_TYPE_TRANSLATION:
        # config.DEEPL_BASE_URL = "https://api.deepl.com/v2/translate"  # paid version
        config.DEEPL_BASE_URL = os.getenv('DEEPL_API_URL') # free version
        config.KEY_HEADER_TEXT_TRANSLATION = "Authorization"
        config.KEY_HEADER_VALUE_TRANSLATION = f"DeepL-Auth-Key {os.getenv('DEEPL_API_KEY') or ''}"

    else:
        raise Exception("Error: Unknown CLOUD_TYPE_TRANSLATION")

    return config
