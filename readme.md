# Mindjet Mindmanager automation and LLM Integration

These automations and macros enhance mindmaps created by **Mindjet Mindmanager**.

## Features

- Supported LLMs:
  - Azure OpenAI Api (use your key) -> ***best tested***
  - OpenAI Api (use your key)
  - Gemini Pro Generative Language Api (use your key)  
  - Gemini Pro Vertex AI Api (use your access token)  
  - Ollama -> ***use zephyr model for best results***
- Windows compatible (run macro/context menu or call the **Python** script directly)  
- MACOS compatible (run **Automator** workflow (Quick Action) or call the **Python** script directly)  
- Just native LLM requests via REST calls (no middleware needed)

## Implemented Use Cases

1. Refinement of the map or topic.  
2. Refinement of the map or topic from a development perspective.  
3. Create examples for one, more (selected) or all topics.  
4. Clustering topics from scratch.  
5. Clustering by one or more criterias eg. Organization/Process/Project/Expertise, Capex-Opex perspective.  
6. Complex cases (multiple calls): eg. refinement + clustering + examples.  

## Examples  
### Windows  
![Example 1](doc/anim2.gif)  

### MACOS
![Example 4 MACOS](doc/anim_macos.gif)  

## Installation  
### Windows  
Run `install.bat` or  
```
pip install --upgrade requests
pip install --upgrade pywin32
```
Macros can be registered directly by merging the `macro_registration.reg` to the registry. Hint: view order in Mindmanager is sorted by the GUIDs. All macros can then be executed using the context menu of topics (right mouse button click).  

![Registry](doc/windows_registry.png)  

Macros can also be executed by the Macro Editor. The macros are similar but the action parameter.  

![Automator](doc/windows_macroeditor.png)  

### MACOS  
```
pip install --upgrade requests
pip install --upgrade appscript
```
Automator workflows can be copied to the Services folder by executing the `copy_to_services.sh` shell script. To make the script executable:
```
chmod +x ./copy_to_services.sh
```  

All **Automator** workflow settings are similar but the action parameter:  

<img src="doc/macos_automator.png" width="600" >

The workflows are then available at the "MindManager" main menu -> Services  

<img src="doc/macos_services.png" width="400" >  


## LLM systems
### Azure OpenAI
The solution ist best tested with `Azure OpenAI`. Results are prefect for every use case. Execution time can take a while.  
### Gemini Pro
`Gemini Pro` results are restrictied by 2k tokens by now and therefore truncated. Usage is not recommended.  
### Ollama
Ollama results are not perfect and dependent on the used model. `Zephyr` brings better results than others eg. `LLama2`. `Mistral` and `Neural-chat` are good as well.

## Configuration  
LLM Api relevant information should be stored in environment variables and mapped to the corresponding variables in the `config.py` file. Not every parameter is used at the moment (token count, levels deep etc.).  

```Python
LOG = True # write source mindmaps, destination mindmaps and prompts to file

SYSTEM_PROMPT = "You are a business consultant and helpful assistant."

# ChatGPT, best in class
CLOUD_TYPE = 'AZURE'                           # best,        uncensored(?)
# CLOUD_TYPE = 'OPENAI'                          # best,        uncensored(?)

# Ollama (local models), best results
# CLOUD_TYPE = 'OLLAMA+mixtral'                  # best,        censored
# CLOUD_TYPE = 'OLLAMA+solar'                    # best,        uncensored
# CLOUD_TYPE = 'OLLAMA+mistral'                  # best,        uncensored
# CLOUD_TYPE = 'OLLAMA+openchat'                 # very good,   uncensored
# CLOUD_TYPE = 'OLLAMA+zephyr'                   # very good,   uncensored *
# CLOUD_TYPE = 'OLLAMA+neural-chat'              # good,        uncensored

# Ollama (local models), not working
# CLOUD_TYPE = 'OLLAMA+mistral-openorca'         # bad,         uncensored
# CLOUD_TYPE = 'OLLAMA+phi'                      # not working
# CLOUD_TYPE = 'OLLAMA+llama2'                   # not working
# CLOUD_TYPE = 'OLLAMA+llama2-uncensored'        # not working
# CLOUD_TYPE = 'OLLAMA+wizard-vicuna-uncensored' # not working
# CLOUD_TYPE = 'OLLAMA+yi'                       # not working

# Gemini (bad results, sometimes not working at all)
# CLOUD_TYPE = 'GEMINI'                          # bad, censored --> error
# CLOUD_TYPE = 'GEMINIPROJECT'                   # bad

LLM_TEMPERATURE = float('0.3')

MAX_TOKENS_SIMPLE = int('100')
MAX_TOKENS_NORMAL = int('1000')
MAX_TOKENS_DEEP = int('4000')
TOP_MOST_RESULTS = int('5')
TOP_MOST_RESULTS_DEEP = int('6')
MAX_RETURN_WORDS = int('5')
LEVELS_DEEP = int('5')

INDENT_SIZE = int('2')
LINE_SEPARATOR = "\n"

if CLOUD_TYPE == "OPENAI":
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_NATIVE')
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_DEPLOYMENT = ""
    OPENAI_API_VERSION = ""

    OPENAI_MODEL = "gpt-4"
    API_URL = OPENAI_API_URL
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + OPENAI_API_KEY

elif CLOUD_TYPE == "AZURE":
    OPENAI_API_KEY = os.getenv('OPENAI2_API_KEY')
    OPENAI_API_URL = os.getenv('OPENAI2_API_BASE')
    OPENAI_DEPLOYMENT = os.getenv('OPENAI2_DEPLOYMENT')
    OPENAI_API_VERSION = os.getenv('OPENAI2_API_VERSION')

    OPENAI_MODEL = ""
    API_URL = f"{OPENAI_API_URL}openai/deployments/{OPENAI_DEPLOYMENT}/chat/completions?api-version={OPENAI_API_VERSION}"
    KEY_HEADER_TEXT = "api-key"
    KEY_HEADER_VALUE = OPENAI_API_KEY

elif CLOUD_TYPE == "GEMINI":
    MODEL_ID = "gemini-pro" # "gemini-pro|gemini-pro-vision"
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY_AI')

    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={GOOGLE_API_KEY}"
    KEY_HEADER_TEXT = ""
    KEY_HEADER_VALUE = ""

elif CLOUD_TYPE == "GEMINIPROJECT":
    MODEL_ID = "gemini-pro" # "gemini-pro|gemini-pro-vision"
    PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID_AI')
    API_ENDPOINT="us-central1-aiplatform.googleapis.com"
    LOCATION_ID="us-central1"
    GOOGLE_ACCESS_TOKEN = os.getenv('GOOGLE_ACCESS_TOKEN_AI')

    API_URL = f"https://{API_ENDPOINT}/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION_ID}/publishers/google/models/{MODEL_ID}:streamGenerateContent"
    KEY_HEADER_TEXT = "Authorization"
    KEY_HEADER_VALUE = "Bearer " + GOOGLE_ACCESS_TOKEN

elif "OLLAMA" in CLOUD_TYPE:
    MODEL_ID = CLOUD_TYPE.split("+")[-1]
    API_URL="http://localhost:11434/api/generate"
```

## Prompt crafting  
Prompt crafting is lightly implemented using the following strategy:  

![Configuration](doc/prompt.png)  

## Platform specific implementations
### Windows  
MindManager COM objects are addressed by using the PyWin32 library:  

<img src="doc/windows_mindmanager.png" height="210" >

### MACOS  
MindManager objects are addressed by using the AppScript library:  

<img src="doc/macos_mindmanager.png" height="200" >

## Implementation details  
The Mermaid mindmap syntax is used when talking to the OpenAI LLM as an intermediate "language". Log file contents for input, output, prompt can be used in other use cases eg. mindmap visualizations in GitHub markdown files.  

![Log](doc/log.png)  

Log files content:  

<img src="doc/log_files.png" width="500" >

Example using a Mermaid mindmap in a (this!) GitHub markdown file.  
Code:
```
```mermaid
mindmap
  Creating an AI Startup
    Market Research
      Identify Target Audience
      Analyze Competitors
      Understand Market Trends
      Assess Market Needs
      Evaluate Market Size
    Business Model
      Define Value Proposition
      Choose Revenue Streams
      Plan Monetization Strategy
      Identify Cost Structure
      Determine Key Partnerships```  
```

Github rendering of the (this!) map:

```mermaid
mindmap
  Creating an AI Startup
    Market Research
      Identify Target Audience
      Analyze Competitors
      Understand Market Trends
      Assess Market Needs
      Evaluate Market Size
    Business Model
      Define Value Proposition
      Choose Revenue Streams
      Plan Monetization Strategy
      Identify Cost Structure
      Determine Key Partnerships 
```

You can also use the content inside the Mermaid online editor (https://mermaid.live/edit):  

![Mermaid](doc/mermaid.png)  


## Disclaimer

The API execution time can be somewhat lengthy, typically around 20 seconds or more per call. For more intricate use cases, this duration can extend to 2 minutes or more, with execution time also varying based on token count.

Currently, this project is in the early development phase, and generated outputs may include errors. Automated testing has not yet been implemented.

Should a runtime error occur, please attempt at least a second call to the process ;-)
