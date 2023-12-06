# Mindjet Mindmanager automation and OpenAI Integration

These automations and macros enhance mindmaps created by **Mindjet Mindmanager**.

## Features

- Windows and MACOS
- On Windows the **Python** logic can be called from a macro or by starting the **Python** script directly   
- On MACOS the **Python** logic can be called by an **Automator** workflow ie. **Quick Action** or by starting the **Python** script directly   
- Utilizes **OPENAI** or **Azure OPENAI** api infrastructure for generation
- Configuration for OpenAI api can be found and modified in `config.py`

## Implemented Use Cases

1. Refinement of the map or topic.  
2. Refinement of the map or topic from development perspective.  
3. Create examples for one, more (selected), all topics.  
4. Clustering topics from scratch.  
5. Clustering by on or more criterias eg. Organization/Prpcess/Project/Expertise, Capex-Opex perspective.  
6. Complex cases (multiple calls): eg. refinement + clustering + examples.  

## Examples  
### Windows  
![Example 1](doc/anim1.gif)  

![Example 2](doc/anim3.gif)  

![Example 3](doc/anim4.gif)  

![Example 3](doc/anim5.gif)  

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

Macros can also be executed by the Macro Editor. The macros are similar but the action parameter:  
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

Automator workflow settings are similar but the action parameter:  

![Automator](doc/macos_automator.png)  

The workflows are then available at the "MindManager" main menu -> Services  

![Services](doc/macos_services.png)  

## Configuration  
OpenAI/AzureOpenAI relevant information should be stored in environment variables and set in the `config-py`. Some parameters are not used at the moment (token count, levels deep etc.).  

![Configuration](doc/config.png)  

## Prompt crafting  
Prompt crafting is lightly implemented using the following strategy:  

![Configuration](doc/prompt.png)  

## Platform specific implementation
### Windows  
MindManager COM objects are addressed by using the PyWin32 library:  

![PyWin32](doc/windows_mindmanager.png)  

### MACOS  
MindManager objects are addressed by using the AppScript library:  

![Appscript](doc/macos_mindmanager.png)  

## Implementation destails
The Mermaid Mindmap syntax is used when talking to the llm. Log outouts can be used in MD files using Mermaid:  

![Mermaid](doc/mermaid.png)  
The online editor is available at https://mermaid.live/edit

Example using a mermaid mindmap with MD on Github:
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
## Disclaimer

This project is in its early stages. Generation might still contain errors. If you encounter an error, please try calling the macro again.
