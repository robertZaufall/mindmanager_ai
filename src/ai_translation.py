import config

import requests
import json

def call_translation_ai(text, language):

    if config.CLOUD_TYPE_TRANSLATION != "":

        # DeepL
        if "DEEPL" in config.CLOUD_TYPE_TRANSLATION:

            # supported languages as source
            # BG,CS,DA,DE,EL,EN,ES,ET,FI,FR,HU,ID,IT,JA,KO,LT,LV,NB,NL,PL,PT,RO,RU,SK,SL,SV,TR,UK,ZH

            # supported languages as target
            # BG.CS.DA.DE.EL.EN-GB.EN-US.ES.ET.FI.FR.HU.ID.IT.JA.KO.LT.LV.NB.NL.PL.PT-BR.PT-PT.RO.RU.SK.SL.SV.TR.UK.ZH
    
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
                headers={
                    "Content-Type": "application/json",
                    config.KEY_HEADER_TEXT_TRANSLATION: config.KEY_HEADER_VALUE_TRANSLATION
                },
                data=json.dumps(payload)
            )
            response_text = response.text
            response_status = response.status_code

            if response_status != 200:
                raise Exception(f"Error: {response_status} - {response_text}")

            parsed_json = json.loads(response_text)
            result = parsed_json['translations'][0]['text']

        return result
