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
![Example 1](doc/anim1.gif)  

![Example 2](doc/anim6.gif)  

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

![Configuration](doc/config.png)  

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

The OpenAI API execution time can be somewhat lengthy, typically around 20 seconds per call. For more intricate use cases, this duration can extend to 2 minutes or more, with execution time also varying based on token count.

Currently, this project is in the early development phase, and generated outputs may include errors. Automated testing has not yet been implemented.

Should a runtime error occur, please attempt at least a second call to the process ;-)
