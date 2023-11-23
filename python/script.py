import sys
import config
import json
import requests
#from openai import OpenAI

# Check if a file argument is provided
if len(sys.argv) > 1:
    file_path = sys.argv[1]
    data = ""
    with open(file_path, 'r') as file:
        data = file.read()

    #client = OpenAI()
    
    str_system = "You are a helpful assistant."
    str_user = ("Given is the following Mermaid mindmap. Please refine each subtopic by adding a new level with "
		"top " + str(config.TOP_MOST_RESULTS) + " most important subtopics, "
		"each subtopic " + str(config.MAX_RETURN_WORDS) + " words at maximum "
		"and return the same Mermaid structure back with two spaces as indentation and no additional text: \n" +
		data.replace("\r", "\n"))

    payload = {
        "max_tokens": config.MAX_TOKENS_DEEP,
        "temperature": config.OPENAI_TEMPERATURE,
        "messages": [
            {"role": "system", "content": str_system},
            {"role": "user", "content": str_user}
        ]
    }
    if config.CLOUD_TYPE == "OPENAI":
        payload["model"] = config.OPENAI_MODEL

    response = requests.post(
        config.API_URL,
        headers={
            "Content-Type": "application/json",
            config.KEY_HEADER_TEXT: config.KEY_HEADER_VALUE
        },
        data=json.dumps(payload)
    )
    response_text = response.text

    parsed_json = json.loads(response_text)
    content = parsed_json["choices"][0]["message"]["content"].replace("```mermaid", "")

    print(content)

else:
    print("No file provided")
