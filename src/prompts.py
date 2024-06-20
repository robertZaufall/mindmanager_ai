import config

prompt_prefix = "Given is the following Mermaid mindmap. "

prompt_postfix = (
    f"Return back the complete mindmap data as a functional Mermaid mindmap using correct Mermaid syntax and using {config.INDENT_SIZE} space characters as topic level delimiters. "
    f"Put also {config.INDENT_SIZE} space characters in front of the first topic i.e. central topic following the 'mermaid' keyword. Don't change or delete CentralTopic topic. "
    f"Don't include the phrase 'central topic' or similar to the central topic. "
    f"Each topic or subtopic must not have more than {config.MAX_RETURN_WORDS} words at maximum. If an existing topic has more than {config.MAX_RETURN_WORDS} words, reduce it to {config.MAX_RETURN_WORDS} words. "
    f"Use the 'mermaid' keyword only once at the beginning or suppress it. They keyword 'mindmap' must be present without any whitespace characters in front of this keyword. "
    f"Don't use only numbers as topics but replace them with something meaningful. "
    f"Do not add any additional text or explainings at the beginning or end to your answer. The answer must be pure Mermaid code only. "
    f"Suppress any text like 'Here is the refined mind map' or else in your answer. "
    f"This is an example of a n level deep mindmap and how the output format has to look like: \n"
    f"'mindmap\n  CentralTopic\n    Topic_1\n      Subtopic_11\n        Subtopic_111\n        ..\n        Subtopic_11n\n      Subtopic_12\n      ..\n      Subtopic_1n\n    Topic_2\n      Subtopic_21\n        Subtopic_211\n    ..\n    Topic_n'\n\n"
    f"Here is the data: \n"
)

def prompt_image(top_most_topic, subtopics):
    explicit_style = f" using {config.EXPLICIT_STYLE} style" if config.EXPLICIT_STYLE != "" else ""
    topics = f" and the subtopics {subtopics}" if subtopics != "" else ""
    str_user = (
        f"A clean, minimalist, professional marketing logo{explicit_style} on a white background with focus on {top_most_topic}{topics}. "
        f"Use a visually appealing and professional look."
    )
    return str_user

def prompt_glossary(text, topic_texts, target_format):
    topics = f"\"{topic_texts}\"" if topic_texts else "the whole map"

    str_user = (
        prompt_prefix +
        f"Please create an alphabetically sorted glossary for {topics} including all business relevant special terms and technical terms and use the whole mindmap in Mermaid syntax as context. "
        f"Eliminate duplicates. "
        f"Add a short explaining of each term in one sentence. "
        f"Use the original used language. "
        f"Don't split terms and its descriptions within the same first character. "
        f"Do not add any additional text or explainings at the beginning or end to your answer. Do not use any technical keyword like 'html' or 'markdown' etc. at the start of the text.\n"
        f"The desired target format is {str.upper(target_format)} and should mimic the following markdown format (also Helvetica font if appropriate for the format): \n# Glossary\n\n## A\n- **A_Term1**: Explanation of Term1\n- **A_Term2**: Explanation of Term2\n\n## B\n- **B_Term1**: Explanation of B_Term1\n...\n"
        #"Use this style tag: <style>body {font-family: Helvetica, Arial, sans-serif;}; h1, h2 {font-weight: bold;}</style>\n"
        #"<h1>Glossary</h1><h2>A</h2><ul><li><strong>A_Term1</strong>: Explanation for A_Term1</li><li><strong>A_Term2</strong>: Explanation for A_Term2</li></ul><h2>B</h2><ul><li><strong>B_Term1</strong>: Explanation for B_Term1</li>...</ul>...\n"
        f"Here is the data: \n" +
        text
    )
    return str_user

def convert_markdown_to_html(title, markdown_text):  
    import markdown
    html_fragment = markdown.markdown(markdown_text)  
    complete_html = f"""
<!DOCTYPE html><html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">  
<title>{title}</title>
<style>body {{font-family: Helvetica, Arial, sans-serif;}}; h1, h2 {{font-weight: bold;}}</style>
</head>
<body>{html_fragment}</body></html>
"""  
    return complete_html  

def prompt_refine(text, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please refine {topics} by adding at least one more additional level with up to {config.TOP_MOST_RESULTS} top most important subtopics, "
        f"but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"Do not change the central topic. "
        f"If there are existing 'examples' topics, include them but do not refine them. If there are no 'examples' topics, don't create any. " +
        prompt_postfix +
        text
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
        text
    )
    return str_user

def prompt_cluster(text, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please rethink, redo, rebalance and recluster the whole map from scratch, "
        f"reduce complexity, simplify topics where possible and meaningful without loosing important information, "
        f"include missing most important topics or remove least import topics if there are any. " +
        prompt_postfix +
        text
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
        text
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
        text
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
        text
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
        text
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
        text
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
        text
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
        text
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
    if   param == "refine":          return prompt_refine(text_input, topic_texts=topic_texts)
    elif param == "refine_dev":      return prompt_refine_dev(text_input, topic_texts=topic_texts)
    elif param == "examples":        return prompt_examples(text_input, topic_texts=topic_texts)
    elif param == "cluster":         return prompt_cluster(text_input, topic_texts=topic_texts)
    elif param == "prc_org":         return prompt_prc_org(text_input, topic_texts=topic_texts)
    elif param == "prj_prc_org":     return prompt_prj_prc_org(text_input, topic_texts=topic_texts)
    elif param == "exp_prj_prc_org": return prompt_exp_prj_prc_org(text_input, topic_texts=topic_texts)
    elif param == "exp":             return prompt_exp(text_input, topic_texts=topic_texts)
    elif param == "prj_org":         return prompt_prj_org(text_input, topic_texts=topic_texts)
    elif param == "capex_opex":      return prompt_capex_opex(text_input, topic_texts=topic_texts)
    else:
        return ""
