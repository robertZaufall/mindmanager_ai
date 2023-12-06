# Mindjet Mindmanager automation and OpenAI Integration

These automations and macros enhance mindmaps created by **Mindjet Mindmanager**.

## Features

- Both platforms: Windows and MACOS
- On Windows written in **Win Wrap Basic** and alternatively in **Win Wrap Basic** combined with **Python** 
- On MACOS written in **Python** using **appscript** and alternatively in pure **Apple Script** (incomplete approach by now)
- Utilizes the **OpenAI REST Api** at **OpenAI** or **Azure OpenAI** for generation
- Configuration for OpenAI Api can be found and modified in `settings.cls` and `config.py`

## Implemented Use Cases

1. Refinement of the map.  
2. Refinement of the map from development perspective.  
3. Create examples for one, more (selected), all topics.  
4. Clustering topics from scratch.  
5. Clustering by on eore more criterias eg. Org/Pc/Prj/Exp, Capex-Opex.  
6. Complex cases (multiple calls): eg. refinement + clustering + examples.  

## Examples

![Example 1](doc/anim1.gif)  

![Example 2](doc/anim3.gif)  

![Example 3](doc/anim4.gif)  


## Disclaimer

This project is in its early stages. Generation might still contain errors. If you encounter an error, please try calling the macro again.
