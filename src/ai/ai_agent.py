import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import ai.ai_llm as ai_llm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import file_helper as fh

def call_agent(agent_file, argument, model, secondary_model):
    agent_path = os.path.join(os.path.dirname(__file__), 'agents', agent_file)
    if not os.path.exists(agent_path):
        raise Exception(f"Error: {agent_file} does not exist.")
    module = fh.load_module_from_path(agent_path, "magent")
    agent = module.MAgent(model, secondary_model)
    result = agent.execute(argument)

    # todo: remove this step - get mermaid from markdown result by calling the LLM model again
    mermaid = ai_llm.call_llm_sequence(model=model, prompts_list=["md2mindmap"], input=result, topic_texts=argument)
    return mermaid