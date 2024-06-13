# MindManager Automation and LLM Integration

These automations and macros enhance mindmaps created by **MindManager** on macOS and Windows.

## Features

### Supported LLMs
  - **Azure OpenAI** w/ ***GPT-4o*** (use your key) -> **best tested**
  - **OpenAI** w/ ***GPT-4o*** (use your key) -> **best results**
  - **Anthropic** w/ ***Claude 3*** (use your key)  
  - **Groq** (platform) w/ ***LLama3*** (use your key)
  - **Perplexity** (platform) w/ ***LLama3*** (use your key)
  - **Google Gemini** w/ ***Pro*** and ***Flash*** (use your key)  
  - **Google Vertex AI** w/ ***Gemini Pro*** and ***Gemini Flash*** (use your access token)
  - **Ollama** (local) w/ any LLM (use ***LLama3***, ***Zephyr*** or ***Mixtral*** model for best results)
  - **MLX** (local w/ Apple Silicon) w/ any LLM (use ***LLama3*** model for best results)

### Platform
- Windows compatible (run macro/context menu or call the **Python** script directly)  
- macOS compatible (run **Automator** workflow (Quick Action) or call the **Python** script directly)  
- Just native LLM requests via API calls - **no middleware needed**

### Layout
- Map format can be radial map or orgchart
- Using map templates on macOS
- Map styles on Windows are persistent, automatic collapsing of nodes

### Supported Image Generation Systems
  - **Azure OpenAI** w/ ***DALL-E-3*** (use your key) -> **best tested**
  - **OpenAI** w/ ***DALL-E-3*** (use your key) -> **best results**
  - **Stability AI** w/ ***Stable Diffusion 3 / Ultra / Core*** (use your key)  

## Implemented Business or Use Cases
1. Refinement of the map or topic.  
2. Refinement of the map or topic from a development perspective.  
3. Create examples for one, more (selected) or all topics.  
4. Clustering topics from scratch.  
5. Clustering by one or more criterias eg. Organization/Process/Project/Expertise, Capex-Opex perspective.  
6. Complex cases (multiple calls): eg. refinement + clustering + examples.  
7. NEW: Image generation with DALL-E-3 from topics (use copy/pase after generation)

## Other Use Cases (implemented or easy to add)
- Export mindmap to Mermaid syntax or any other text format
- Change map layout by using a template (macOS)
- Reorder topics by business value or importance
- Translate the map to other languages
- Misspelling or syntax correction
- Create a map based on external text data

## Examples  
### Windows  
![Example 1](doc/anim2.gif)  

### macOS
![Example 4 macOS](doc/anim_macos.gif)  

## Installation  
### Windows  
Python has to be installed first (eg. using Chocolatey).  
Run `install.bat` or  
```
pip install --upgrade requests
pip install --upgrade pywin32
```
Macros can be registered directly by merging the `macro_registration.reg` to the registry. Hint: view order in MindManager is sorted by the GUIDs. All macros can then be executed using the context menu of topics (right mouse button click).  

![Registry](doc/windows_registry.png)  

Macros can also be executed by the Macro Editor. The macros are similar but the action parameter.  

![Automator](doc/windows_macroeditor.png)  

### macOS  
Python has to be installed first (eg. using Homebrew).  
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

## How to use  
### Map actions
Select the central topic or deselect all topics and call the macro by right-clicking (Windows) or by choosing the Automator Action via the MindManager menu -> Services -> General. You can also select one or more topics and start the automation.
### Image generation
Image generation has been tested only on macOS so far. Just select the topics for which you want to generate an image and choose the action "Generate Image" or call a defined macro or the Python script. After a little while, the image will be opened and also stored in the `src/images` folder. Unfortunately, the image cannot automatically be inserted into the map or added to a topic due to insufficient library support on macOS. The results from the generation process are good with DALL-E 3 and sometimes not as good with Stable Diffusion. Prompt crafting/engineering is still in progress.

## LLM systems
### Azure OpenAI / OpenAI
The solution ist best tested with `Azure OpenAI`. Results are perfect but slow for every use case. Execution time is far better with `OpenAI / GPT-4o`.  
### Google Gemini / Vertex AI
`Gemini Pro` results are good. `Gemini Flash` does (most of the time) only generate up to 3 levels at max, so a refinement does currently not work.  
### Ollama (hosted locally - no internet access needed)
Ollama results are dependent on the used model. `LLama3`, `Zephyr` and `Mixtral` are working well.  
### Anthropic Claude 3
Anthropic Claude 3 results are ogood. The OPUS model is a little bit expensive.
### groq (platform)
groq is sure the fastest LLM platform by now. Payment for API usage is still unclear because there is no way to set a payment method (as of 2024-05-05).  
### Perplexity (platform)
Perplexity works perfekt as an univeral LLM platform.  
### MLX (hosted locally on Apple Silicon - no internet access needed)
MLX results are dependent on the used model. `LLama3` works well.

## Configuration  
All configuration is stored in the `config.py` file. Security relevant information should be mapped using environment variables.  
Don't be overwhelmed by the huge list of variables. Just pick the lines you need and set its values  

## Prompt crafting  
Prompt crafting is lightly implemented using the following strategy:  

![Configuration](doc/prompt.png)  

## Platform specific implementations
### Windows  
MindManager COM objects are addressed by using the PyWin32 library:  

<img src="doc/windows_mindmanager.png" height="210" >

### macOS  
MindManager objects are addressed by using the AppScript library:  

<img src="doc/macos_mindmanager.png" height="200" >

## Implementation details  
The Mermaid mindmap syntax is used when talking to the OpenAI LLM as an intermediate "language". Log file contents for input, output, prompt can be used in other use cases eg. mindmap visualizations in GitHub markdown files.  

![Log](doc/log.png)  

Log files content:  

<img src="doc/log_files.png" width="500" >

Example using a Mermaid mindmap in a GitHub markdown file.  
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

Github rendering of the map:

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
The API execution time depends heavily on the used LLM model or system and token count.  

Currently, this project is in the early development phase, and generated outputs may include errors. Automated testing has not yet been implemented.  
