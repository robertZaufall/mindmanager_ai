import config

prompt_prefix = "Given is the following Mermaid mindmap. "

prompt_postfix = (
    f"Return back the complete mindmap data as a functional Mermaid mindmap using correct Mermaid syntax and using {config.INDENT_SIZE} space characters as topic level delimiters. "
    f"Put also {config.INDENT_SIZE} space characters in front of the first topic i.e. central topic. Use the 'mermaid' keyword only once at the beginning. "
    f"Do not add any additional text or explainings to your answer. "
    f"This is an example of a n level deep mindmap: \n"
    f"'mindmap\n  CentralTopic\n    Topic_1\n      Subtopic_11\n        Subtopic_111\n        ..\n        Subtopic_11n\n      Subtopic_12\n      ..\n      Subtopic_1n\n    Topic_2\n      Subtopic_21\n        Subtopic_211\n    ..\n    Topic_n'\n "
    f"Here is the data: \n"
)

def prompt_refine(text, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please refine {topics} by adding an additional n+1 level of deepness with up to {config.TOP_MOST_RESULTS} top most important subtopics, "
        f"but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"Each subtopic must not have more than {config.MAX_RETURN_WORDS} words at maximum. "
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
        f"Please refine {topics} by adding an additional n+1 level of deepness with up to {config.TOP_MOST_RESULTS} top most important subtopics from a software development perspective, "
        f"but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"Each subtopic must not have more than {config.MAX_RETURN_WORDS} words at maximum. "
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
    if   param == "complexity_1": return ["refine", "cluster", "examples"]
    elif param == "complexity_2": return ["exp_prj_prc_org", "refine"]
    elif param == "complexity_3": return ["exp_prj_prc_org", "refine", "examples"]
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
