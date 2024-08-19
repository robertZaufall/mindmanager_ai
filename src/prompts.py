import config

prompt_prefix = "Given is the following Mermaid mindmap. "
prompt_prefix_text = "Given is the following text to be summarized as a mindmap with Mermaid syntax. "

prompt_postfix = (
    f"Return back the complete mindmap data as a functional Mermaid mindmap using correct Mermaid syntax and using {config.INDENT_SIZE} space characters as topic level delimiters. "
    f"Put also {config.INDENT_SIZE} space characters in front of the first topic i.e. central topic following the 'mermaid' keyword. Don't change or delete CentralTopic topic. "
    f"Don't include the phrase 'central topic' or similar to the central topic. "
    f"Each topic or subtopic must not have more than {config.MAX_RETURN_WORDS} words at maximum. If an existing topic has more than {config.MAX_RETURN_WORDS} words, reduce it to {config.MAX_RETURN_WORDS} words. "
    f"Use the 'mermaid' keyword only once at the beginning or suppress it. They keyword 'mindmap' must be present without any whitespace characters in front of this keyword. "
    f"Don't use only numbers as topics but replace them with something meaningful. "
    f"Do not add any additional text or explainings at the beginning or end to your answer. The answer must be pure Mermaid code only. "
    f"Suppress any text like 'Here is the refined mind map' or else in your answer. "
    f"Don't add 'Here is the refined mind map in Mermaid syntax:' or 'Here is the mindmap in Mermaid syntax based on the summary:' or any other text to your answer, but just the code. "
    f"This is an example of a n level deep mindmap and how the output format has to look like: \n"
    f"```mindmap\n  CentralTopic\n    Topic_1\n      Subtopic_11\n        Subtopic_111\n        ..\n        Subtopic_11n\n      Subtopic_12\n      ..\n      Subtopic_1n\n    Topic_2\n      Subtopic_21\n        Subtopic_211\n    ..\n    Topic_n```\n\n"
    f"Here is the data: \n"
)

def prompt_image(top_most_topic, subtopics):
    explicit_style = f" using {config.EXPLICIT_STYLE} style" if config.EXPLICIT_STYLE != "" else ""
    topics = f" and the subtopics {subtopics}" if subtopics != "" else ""
    str_user = (
        f"A clean, minimalistic, professional marketing logo{explicit_style} on a white background with focus on {top_most_topic}{topics}. "
        f"Use a visually appealing and professional look."
    )
    return str_user

def prompt_image_sd(top_most_topic, subtopics):
    explicit_style = f" using {config.EXPLICIT_STYLE} style" if config.EXPLICIT_STYLE != "" else ""
    topics = f" and also influenced by thought of {subtopics}" if subtopics != "" else ""
    str_user = (
        f"One professional graphic, minimalistic, professional{explicit_style} on a white background about {top_most_topic}{topics}. "
        f"Use an outstanding, visually appealing, high-detailed, polished and expensive look."
    )
    return str_user

def prompt_image_flux(top_most_topic, subtopics):
    explicit_style = f" using {config.EXPLICIT_STYLE} style" if config.EXPLICIT_STYLE != "" else ""
    topics = f" and also influenced by thought of {subtopics}" if subtopics != "" else ""
    str_user = (
        f"Business graphic, minimalistic, professional{explicit_style} on a mostly white background full-filled with typical big symbols or a strong scene representing {top_most_topic}{topics}. "
        f"Outstanding, visually appealing, polished and expensive look and finish. No text."
    )
    return str_user

def prompt_image_prompt(text):
    str_user = (
        f"Please optimize this prompt to generate a good marketing logo like image or pictogram on a white background without gradient "
        f"using Stable Diffusion 2: ```{text}```\n "
        f"Return only the prompt without any further text or explainings."
    )
    return str_user

def prompt_glossary(text, topic_texts):
    message = "Please create a glossary of embedded business-relevant special terms and technical terms or phrases "
    if topic_texts != "":
        main_message = message + f"only included in this string: \"{topic_texts}\". Use the attached mindmap in Mermaid syntax just as context. "
        context = "context"
    else:
        main_message = message + "included in the whole attached mindmap in Mermaid syntax. "
        context = "data"

    str_user = (
        main_message +
        f"Ensure the following: \n"
        f" 1. Eliminate duplicate lines in your answer. \n"
        f" 2. Provide a one-sentence explanation for each term. \n"
        f" 3. Group the terms or phrases by its first chracter. \n"
        f" 4. Sort the groups alphabetically. \n"
        f" 5. Combine groups with the same character. Don't split character-groups. \n"
        f" 6. Eliminate any '_' in your answer. \n"
        f" 7. Do not include any additional text or explanations at the beginning or end of your answer. \n"
        f" 8. Don't output the keywords 'html' or 'markdown' at the start of your text. \n"
        f" 9. Check twice if the glossary is sorted alphabetically. \n"
        f"10. If there is no special term or phase for a character, just ignore this. Don't express this state. \n"
        f"The desired target format is MARKDOWN and should mimic the following markdown format (also Helvetica font if appropriate for the format): \n"
        f"`\n# Glossary\n\n## A\n- **A_Term1**: Explanation of Term1\n- **A_Term2**: Explanation of Term2\n\n## B\n- **B_Term1**: Explanation of B_Term1\n...\n`\n\n"
        f"Here is the {context}: \n" +
        f"`\n{text}`"
    )
    return str_user

def prompt_glossary_optimize(text):
    str_user = (
        f"Given is a glossary to be optimized by you. Ensure the following: \n"
        f" 1. Non-technical or non-business relevant or trivial terms and phrases are removed. \n"
        f" 2. Every term or phrase is explained, not only repeated. \n"
        f" 3. Every term or phrase is explained in exactly one sentence. \n"
        f" 4. Terms or phrases are grouped by the first chracter. \n"
        f" 5. Each term or phrase is in its correct group. \n"
        f" 6. Groups are not split. \n"
        f" 7. All groups are sorted alphabetically. \n"
        f" 8. There are not keywords like 'html' or 'markdown' at the start of the content. \n"
        f" 9. There is not prefix for the terms or phrases like 'A_', 'B_'. \n"
        f"Don't add any additional text, explainings or comments at the beginning or end to your answer like 'Here is the optimized (...)'. \n"
        f"Here is the glossary: \n" +
        f"'\n{text}'"
    )
    return str_user

def prompt_refine(text, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please refine {topics} by adding at least one more additional level with up to {config.TOP_MOST_RESULTS} top most important subtopics, "
        f"but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"Do not change the central topic. "
        f"If there are existing 'examples' topics, include them but do not refine them. If there are no 'examples' topics, don't create any. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_refine_dev(text, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please refine {topics} by adding at least one more additional level with up to {config.TOP_MOST_RESULTS} top most important subtopics from a software development perspective, "
        f"but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"Do not change the central topic. "
        f"If there are existing 'examples' topics, include them but do not refine them. If there are no 'examples' topics, don't create any. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_cluster(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please rethink, redo, rebalance and recluster the whole map from scratch, "
        f"reduce complexity, simplify topics where possible and meaningful without loosing important information, "
        f"include missing most important topics or remove least import topics if there are any. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_prc_org(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        f"dividing organizational topics ('organization') vs. process oriented topics ('process'), "
        f"include missing most important topics or remove least import topics if there are any, "
        f"avoid duplicate topics and generalize or abstract more where applicable. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_prj_prc_org(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        f"dividing organizational topics ('organization') vs. process oriented topics ('process') vs project management oriented topics ('project'), "
        f"include missing most important topics or remove least import topics if there are any, "
        f"avoid duplicate topics and generalize or abstract more where applicable. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_exp_prj_prc_org(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        f"dividing organizational topics of this top level business case ('organization') vs. "
        f"process oriented topics of this top level business case ('process') vs. "
        f"project management oriented topics of this top level business case ('project') vs. "
        f"center of excellence oriented topics of this top level business case ('expertise'), "
        f"include missing most important topics or remove least import topics if there are any, "
        f"avoid duplicate topics and generalize or abstract more where applicable. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_exp(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please recluster all topics of the whole map from scratch to 4 levels at maximum regarding "
        f"expertiese and center of excellence oriented topics and from a strong top level business case centric perspective, "
        f"include missing most important topics or remove least import topics if there are any, "
        f"avoid duplicate topics and generalize or abstract more where applicable. " +
        prompt_postfix +
        f"```\n{text}\n```"
    )
    return str_user

def prompt_capex_opex(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        f"dividing capex oriented topics ('capex') vs. opex oriented topics ('opex'), "
        f"include missing most important topics or remove least import topics if there are any, "
        f"avoid duplicate topics and generalize or abstract more where applicable. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_prj_org(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        f"dividing topics regarding the organizational structure (organization') vs. project management oriented topics ('project'), "
        f"include missing most important topics or remove least import topics if there are any, "
        f"avoid duplicate topics and generalize or abstract more where applicable. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_examples(text, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please add for {topics} a new subtopic 'examples' if not existant yet, "
        f"and add a new level with up to {config.TOP_MOST_RESULTS} top most important examples or extend the existing ones, "
        f"with each example {config.MAX_RETURN_WORDS} words at maximum. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_text_to_mindmap(text, topic_texts=""):
    central_topic = f"\"{topic_texts}\"" if topic_texts else "an expression of 1-3 words the text is about"

    str_user = (
        prompt_prefix_text +
        f"Please create a mindmap from the summary using '{topic_texts}' as central topic, "
        f"add at least 2 levels with up to {config.TOP_MOST_RESULTS} top most important topics each. " +
        f"For each topic generate a usefull and sensible text without unnecessary abbreviations. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompt_text_to_knowledgegraph(text, topic_texts=""):
    str_user = (
        f"Please create a knowledge graph from the following text and return it in valid mermaid syntax. Don't add any additional text or explainings. "
        f"```\n{text}```"
    )
    return str_user

def prompt_knowledgegraph_to_mindmap(text, topic_texts=""):
    str_user = (
        f"Please create a mindmap from the following mermaid graph data and return it in valid mermaid syntax. Don't add any additional text or explainings. " +
        prompt_postfix +
        f"```\n{text}```"
    )
    return str_user

def prompts_list_from_param(param):
    if   param == "complexity_1": return ["refine", "refine", "cluster"]
    elif param == "complexity_2": return ["exp_prj_prc_org", "refine"]
    elif param == "complexity_3": return ["prj_prc_org", "refine"]
    else:
        return [param]

def prompt(param, text, topic_texts=""):
    text_input = text.replace("\r", "\n")
    if   param == "refine":                 return prompt_refine(text_input, topic_texts=topic_texts)
    elif param == "refine_dev":             return prompt_refine_dev(text_input, topic_texts=topic_texts)
    elif param == "examples":               return prompt_examples(text_input, topic_texts=topic_texts)
    elif param == "cluster":                return prompt_cluster(text_input, topic_texts=topic_texts)
    elif param == "prc_org":                return prompt_prc_org(text_input, topic_texts=topic_texts)
    elif param == "prj_prc_org":            return prompt_prj_prc_org(text_input, topic_texts=topic_texts)
    elif param == "exp_prj_prc_org":        return prompt_exp_prj_prc_org(text_input, topic_texts=topic_texts)
    elif param == "exp":                    return prompt_exp(text_input, topic_texts=topic_texts)
    elif param == "prj_org":                return prompt_prj_org(text_input, topic_texts=topic_texts)
    elif param == "capex_opex":             return prompt_capex_opex(text_input, topic_texts=topic_texts)
    elif param == "glossary":               return prompt_glossary(text_input, topic_texts=topic_texts)
    elif param == "text2mindmap":           return prompt_text_to_mindmap (text_input, topic_texts=topic_texts)
    elif param == "text2knowledgegraph":    return prompt_text_to_knowledgegraph (text_input, topic_texts=topic_texts)
    elif param == "knowledgegraph2mindmap": return prompt_knowledgegraph_to_mindmap (text_input, topic_texts=topic_texts)
    else:
        return ""
