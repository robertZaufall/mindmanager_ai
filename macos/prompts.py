import config

prompt_prefix = "Given is the following Mermaid mindmap. "

prompt_postfix = (
    f"Return back the mindmap data in pure Mermaid mindmap syntax using 2 space characters as topic level delimiters with no additional text or explainings in your answer, "
    f"eg. 'mindmap\n  Central topic\n    Main topic 1\n      Subtopic 11\n      Subtopic 12\n    Main topic 2\n      Subtopic 21\n      Subtopic 22'\n "
    f"Here is the data: \n"
)

def prompt_refine(text, top_most_results, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please refine {topics} by adding a new level with top {top_most_results} most important subtopics, "
        f"but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"Each subtopic must not have more than {config.MAX_RETURN_WORDS} words at maximum. "
        f"Do not change the central topic. "
        f"If there are existing 'examples' topics, include them but do not refine them. If there are no 'examples' topics, don't create any. " +
        prompt_postfix +
        text
    )
    return str_user

def prompt_refine_dev(text, top_most_results, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please refine {topics} by adding a new level with top {top_most_results} most important subtopics from a software development perspective, "
        f"but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"Each subtopic must not have more than {config.MAX_RETURN_WORDS} words at maximum. "
        f"Do not change the central topic. "
        f"If there are existing 'examples' topics, include them but do not refine them. If there are no 'examples' topics, don't create any. " +
        prompt_postfix +
        text
    )
    return str_user

def prompt_cluster(text, top_most_results, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please rethink, redo, rebalance and recluster the whole map from scratch, "
        f"reduce complexity, simplify topics where possible and meaningful without loosing important information, "
        f"include missing most important topics or remove least import topics if there are any. " +
        prompt_postfix +
        text
    )
    return str_user

def prompt_prc_org(text, top_most_results, topic_texts=""):
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

def prompt_prj_prc_org(text, top_most_results, topic_texts=""):
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

def prompt_exp_prj_prc_org(text, top_most_results, topic_texts=""):
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

def prompt_exp(text, top_most_results, topic_texts=""):
    str_user = (
        prompt_prefix +
        f"Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        f"dividing organizational topics ('organization') vs. "
        f"center of excellence oriented topics of this top level business case ('expertise'), "
        f"include missing most important topics or remove least import topics if there are any, "
        f"avoid duplicate topics and generalize or abstract more where applicable. " +
        prompt_postfix +
        text
    )
    return str_user

def prompt_capex_opex(text, top_most_results, topic_texts=""):
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

def prompt_prj_org(text, top_most_results, topic_texts=""):
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

def prompt_examples(text, top_most_results, topic_texts=""):
    topics = f"only the topic(s) \"{topic_texts}\" each" if topic_texts else "each subtopic"

    str_user = (
        prompt_prefix +
        f"Please add for {topics} a new subtopic 'examples' if not existant yet, "
        f"and add a new level with the top {top_most_results} most important examples or extend the existing ones, "
        f"with each example {config.MAX_RETURN_WORDS} words at maximum. " +
        prompt_postfix +
        text
    )
    return str_user

def prompt(param, text, top_most_results, topic_texts=""):
    text_input = text.replace("\r", "\n")
    if param == "refine":
        return prompt_refine(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "refine_dev":
        return prompt_refine_dev(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "examples":
        return prompt_examples(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "cluster":
        return prompt_cluster(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "prc_org":
        return prompt_prc_org(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "prj_prc_org":
        return prompt_prj_prc_org(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "exp_prj_prc_org":
        return prompt_exp_prj_prc_org(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "exp":
        return prompt_exp(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "prj_org":
        return prompt_prj_org(text_input, top_most_results, topic_texts=topic_texts)
    elif param == "capex_opex":
        return prompt_capex_opex(text_input, top_most_results, topic_texts=topic_texts)
    else:
        return ""

