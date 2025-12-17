from __future__ import annotations

from dataclasses import dataclass

import sys
if sys.platform.startswith('win'):
    platform = "win"
elif sys.platform.startswith('darwin'):
    platform = "darwin"

@dataclass(frozen=True)
class PromptSettings:
    """Base configuration for prompt construction."""

    indent_size: int = 2
    max_return_words: int = 5
    top_most_results: int = 5
    levels_deep: int = 5
    line_separator: str = "\n"


DEFAULT_SETTINGS = PromptSettings()

INDENT_SIZE = DEFAULT_SETTINGS.indent_size
MAX_RETURN_WORDS = DEFAULT_SETTINGS.max_return_words
TOP_MOST_RESULTS = DEFAULT_SETTINGS.top_most_results
LEVELS_DEEP = DEFAULT_SETTINGS.levels_deep
LINE_SEPARATOR = DEFAULT_SETTINGS.line_separator

prompt_prefix = "Given is the following Mermaid mindmap. "
prompt_prefix_text = "Given is the following text to be summarized as a mindmap with Mermaid syntax. "


def _build_prompt_postfix(settings: PromptSettings, include_data_header: bool = True) -> str:
    data_header = "Here is the data: \n" if include_data_header else ""
    return (
        f"Return the complete mindmap data as a functional Mermaid mindmap using correct Mermaid syntax and using {settings.indent_size} space characters as topic level delimiters. "
        f"Put also {settings.indent_size} space characters in front of the first topic, i.e. central topic following the 'mermaid' keyword. Don't change or delete CentralTopic topic. "
        "Don't include the phrase 'central topic' or similar to the central topic. "
        f"Each topic or subtopic must not have more than {settings.max_return_words} words at maximum. If an existing topic has more than {settings.max_return_words} words, "
        f"reduce it to {settings.max_return_words} words in a meaningful manner. "
        "Use the 'mermaid' keyword only once at the beginning or suppress it. The keyword 'mindmap' must be present without any whitespace characters in front of this keyword. "
        "There must be no whitespace in front of the 'mermaid' keyword. "
        "Don't use only numbers as topics but replace them with something meaningful. "
        "Do not add any additional text or explanations at the beginning or end to your answer. The answer must be pure Mermaid code only. "
        "Suppress any text like 'Here is the refined mind map' or else in your answer. "
        "Don't stop content generation and don't generate unfinished or placeholder topics like '..'. "
        "Don't add 'Here is the refined mind map in Mermaid syntax:' or 'Here is the mindmap in Mermaid syntax based on the summary:' or any other text to your answer, but just the code. "
        "Check twice if the Mermaid code is syntactically correct: level indentation for every line must be exactly 2 spaces ('  ') also for the first and second topic. Don't use '\\t' or '\t'. "
        "This is an example of an n level deep mindmap and how the output format has to look like: \n"
        "```\nmindmap\n  CentralTopic\n    Topic_1\n      Subtopic_11\n        Subtopic_111\n        ..\n        Subtopic_11n\n      Subtopic_12\n      ..\n      Subtopic_1n\n    Topic_2\n      Subtopic_21\n        Subtopic_211\n    ..\n    Topic_n```\n\n"
        f"{data_header}"
    )


prompt_postfix = _build_prompt_postfix(DEFAULT_SETTINGS)
prompt_postfix_without_data = _build_prompt_postfix(DEFAULT_SETTINGS, include_data_header=False)

REFINE_SUFFIX = (
    "Do not change the central topic which is the top most topic. "
    "If there are existing 'examples' topics, include them but do not refine them. If there are no 'examples' topics, don't create any. "
)

RECLUSTER_SUFFIX = (
    "include missing most important topics or remove least important topics if there are any, "
    "avoid duplicate topics and generalize or abstract more where applicable. "
    "Do not change the central topic which is the top most topic. "
)


def _normalize_text(text: str) -> str:
    return text.replace("\r", "\n")


def _topic_scope(topic_texts: str, scoped_template: str, default: str) -> str:
    return scoped_template.format(topic_texts=topic_texts) if topic_texts else default


def _mermaid_prompt(
    instruction: str,
    text: str,
    *,
    prefix: str = prompt_prefix,
    postfix: str = prompt_postfix,
    end_with_newline: bool = False,
) -> str:
    closing_fence = "\n```" if end_with_newline else "```"
    return f"{prefix}{instruction}{postfix}```\n{_normalize_text(text)}{closing_fence}"


def _recluster_prompt(text: str, lead: str, **mermaid_kwargs) -> str:
    return _mermaid_prompt(f"{lead}{RECLUSTER_SUFFIX}", text, **mermaid_kwargs)


def _topic_context_message(topic_texts: str, scoped_message: str, default_message: str) -> tuple[str, str]:
    if topic_texts:
        return scoped_message.format(topic_texts=topic_texts), "context"
    return default_message, "data"


def prompt_glossary(text: str, topic_texts: str) -> str:
    """Create a glossary anchored to topics inside the supplied mindmap."""
    scoped = (
        'Please create a glossary of embedded business-relevant special terms and technical terms or phrases '
        'only included in this string: "{topic_texts}". Use the attached mindmap in Mermaid syntax just as context. '
    )
    default = (
        "Please create a glossary of embedded business-relevant special terms and technical terms or phrases "
        "included in the whole attached mindmap in Mermaid syntax. "
    )
    main_message, context = _topic_context_message(topic_texts, scoped, default)
    normalized_text = _normalize_text(text)

    return (
        main_message
        + "Ensure the following: \n"
        " 1. Eliminate duplicate lines in your answer. \n"
        " 2. Provide a one-sentence explanation for each term. \n"
        " 3. Group the terms or phrases by their first character. \n"
        " 4. Sort the groups alphabetically. \n"
        " 5. Combine groups of the same character. Don't split character-groups. \n"
        " 6. Eliminate any '_' in your answer. \n"
        " 7. Do not include any additional text or explanations at the beginning or end of your answer. \n"
        " 8. Don't output the keywords 'html' or 'markdown' at the start of your text. \n"
        " 9. Check twice if the glossary is sorted alphabetically. \n"
        "10. If there is no special term or phrase for a character, just ignore this. Don't express this state. \n"
        "The desired target format is MARKDOWN and should mimic the following markdown format (also Helvetica font if appropriate for the format): \n"
        "```\n# Glossary\n\n## A\n- **A_Term1**: Explanation of Term1\n- **A_Term2**: Explanation of Term2\n\n## B\n- **B_Term1**: Explanation of B_Term1\n...\n```\n\n"
        f"Here is the {context}: \n"
        f"```\n{normalized_text}\n```"
    )


def prompt_glossary_optimize(text: str) -> str:
    """Optimize an existing glossary."""
    normalized_text = _normalize_text(text)
    return (
        "Given is a glossary to be optimized by you. Ensure the following: \n"
        " 1. Non-technical or non-business relevant or trivial terms and phrases are removed. \n"
        " 2. Every term or phrase is explained, not only repeated. \n"
        " 3. Every term or phrase is explained in exactly one sentence. \n"
        " 4. Terms or phrases are grouped by the first character. \n"
        " 5. Each term or phrase is in its correct group. \n"
        " 6. Groups are not split. \n"
        " 7. All groups are sorted alphabetically. \n"
        " 8. There are no keywords like 'html' or 'markdown' at the start of the content. \n"
        " 9. There is no prefix for the terms or phrases like 'A_', 'B_'. \n"
        "Don't add any additional text, explanations or comments at the beginning or end of your answer like 'Here is the optimized (...)'. \n"
        "Here is the glossary: \n"
        f"```\n{normalized_text}\n```"
    )


def prompt_argumentation(text: str, topic_texts: str) -> str:
    """Create a structured argumentation based on the supplied mindmap."""
    scoped = (
        'Please create a structured argumentation following exactly the given hierarchy only included in this string: "{topic_texts}". '
        "Use the attached mindmap in Mermaid syntax just as context. "
    )
    default = "Please create a structured argumentation following exactly the given hierarchy included in the whole attached mindmap in Mermaid syntax. "
    main_message, context = _topic_context_message(topic_texts, scoped, default)
    normalized_text = _normalize_text(text)

    return (
        main_message
        + "Ensure the following: \n"
        " 1. Eliminate duplicate topics. \n"
        " 2. Use the predominant language of the whole map for the argumentation text generation. \n"
        " 3. Provide a short argumentation including point, evidence, explanation using at least two sentences for each and every topic. \n"
        " 4. For each topic with subtopics \n"
        "    - output a short summarization of the immediate subtopics \n"
        "    - then go on with argumenting for the subtopics. \n"
        " 5. Don't explicitly output 'point', 'evidence', 'explanation' or their corresponding language equivalents. \n"
        " 6. Don't output the keywords 'html' or 'markdown' at the start of your text. \n"
        " 7. Separate each hierarchy level and separate each topic (new line, number formatting) by its corresponding markdown formatting. \n"
        " 8. Don't forget the summarizations for topics with subtopics. \n"
        " 9. Don't stop generating until all topics are really processed. \n"
        "The desired target format is MARKDOWN (also Helvetica font if appropriate for the format). \n"
        f"Here is the {context}: \n"
        f"```\n{normalized_text}```"
    )


def _refine_prompt(text: str, topic_texts: str, *, level_label: str, perspective: str | None = None) -> str:
    topics = _topic_scope(
        topic_texts,
        scoped_template='only the topic(s) "{topic_texts}" each',
        default="each subtopic",
    )
    perspective_suffix = f" from a {perspective} perspective" if perspective else ""
    instruction = (
        f"Please refine {topics} by adding at least one more additional {level_label} with up to {TOP_MOST_RESULTS} top most important subtopics{perspective_suffix}, "
        "but if you decide from your knowledge there have to be more or fewer most important subtopics, you can increase or decrease this number. "
        f"{REFINE_SUFFIX}"
    )
    return _mermaid_prompt(instruction, text)


def _answer_prompt(text: str, topic_texts: str, *, level_label: str, perspective: str | None = None) -> str:
    topics = _topic_scope(
        topic_texts,
        scoped_template='only the topic(s) "{topic_texts}" each',
        default="each subtopic",
    )
    perspective_suffix = f" from a {perspective} perspective" if perspective else ""
    instruction = (
        "Please "
        "_answer_ (if leaf topics like ['current','actual','now',...]  or ['stocks','price','date','weather',...])  or "
        "_define_ (if leaf topics like ['reason','ground','definition','explanation',...]) "
        f"{topics} "
        f"by adding at least one more additional {level_label} with up to {TOP_MOST_RESULTS} top most important subtopics{perspective_suffix}. "
        "If there are keywords like ['each','every','all',...] in the topic texts, please do it for each of them ([entities,symbols,...]). "
        f"{ "Add representative emojis to leaf topics where appropriate like price differences (up/down) or sentiment. Don't use technical but general emojis, like positive, negative, up, down, extraordinary, (...). " if platform == "darwin" else ""}" 
        "If you decide from your knowledge there have to be more or fewer most important subtopics as essential information, you can increase or decrease this number. "
        f"{REFINE_SUFFIX}"
    )
    return _mermaid_prompt(instruction, text)


def prompt_refine(text: str, topic_texts: str = "") -> str:
    """Refine by adding a deeper child level."""
    return _refine_prompt(text, topic_texts, level_label="child level")


def prompt_answer(text: str, topic_texts: str = "") -> str:
    """Answer by adding a deeper child level."""
    return _answer_prompt(text, topic_texts, level_label="child level")


def prompt_refine_dev(text: str, topic_texts: str = "") -> str:
    """Refine from a software development perspective."""
    return _refine_prompt(
        text,
        topic_texts,
        level_label="level",
        perspective="software development",
    )


def prompt_freetext(text: str, freetext: str, topic_texts: str = "") -> str:
    """Apply a freeform instruction to the supplied mindmap."""
    sanitized_freetext = freetext.replace('"', "`").replace("'", "`").replace("\r", "").replace("\n", "")
    topics = f'only the topic(s) "{topic_texts}" ' if topic_texts else "to the whole mindmap"
    instruction = (
        f"Please do the following action or actions '{sanitized_freetext}' to {topics}. "
        "Do not change the central topic which is the top most topic until you are told todo so. "
    )
    return _mermaid_prompt(instruction, text)


def prompt_cluster(text: str, topic_texts: str = "") -> str:
    """Rebalance and recluster the entire map."""
    del topic_texts  # unused but kept for signature compatibility
    lead = (
        "Please rethink, redo, rebalance and recluster the whole map from scratch, "
        "reduce complexity, simplify topics where possible and meaningful without losing important information, "
    )
    return _recluster_prompt(text, lead)


def prompt_prc_org(text: str, topic_texts: str = "") -> str:
    """Recluster into process vs organization dimensions."""
    del topic_texts
    lead = (
        "Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        "dividing organizational topics ('organization') vs. process oriented topics ('process'), "
    )
    return _recluster_prompt(text, lead)


def prompt_prj_prc_org(text: str, topic_texts: str = "") -> str:
    """Recluster into process vs organization vs project management dimensions."""
    del topic_texts
    lead = (
        "Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        "dividing organizational topics ('organization') vs. process oriented topics ('process') vs project management oriented topics ('project'), "
    )
    return _recluster_prompt(text, lead)


def prompt_exp_prj_prc_org(text: str, topic_texts: str = "") -> str:
    """Recluster including expertise, process, project, and organization views."""
    del topic_texts
    lead = (
        "Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        "dividing organizational topics of this top level business case ('organization') vs. "
        "process oriented topics of this top level business case ('process') vs. "
        "project management oriented topics of this top level business case ('project') vs. "
        "center of excellence oriented topics of this top level business case ('expertise'), "
    )
    return _recluster_prompt(text, lead)


def prompt_exp(text: str, topic_texts: str = "") -> str:
    """Recluster focusing on expertise and centers of excellence."""
    del topic_texts
    lead = (
        "Please recluster all topics of the whole map from scratch to 4 levels at maximum regarding "
        "expertise and center of excellence oriented topics and from a strong top level business case centric perspective, "
    )
    return _recluster_prompt(text, lead, end_with_newline=True)


def prompt_capex_opex(text: str, topic_texts: str = "") -> str:
    """Separate topics into capex vs. opex clusters."""
    del topic_texts
    lead = (
        "Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        "dividing capex oriented topics ('capex') vs. opex oriented topics ('opex'), "
    )
    return _recluster_prompt(text, lead)


def prompt_prj_org(text: str, topic_texts: str = "") -> str:
    """Recluster into organization vs. project management clusters."""
    del topic_texts
    lead = (
        "Please recluster all topics of the whole map from scratch to 4 levels at maximum, "
        "dividing topics regarding the organizational structure ('organization') vs. project management oriented topics ('project'), "
    )
    return _recluster_prompt(text, lead)


def prompt_examples(text: str, topic_texts: str = "") -> str:
    """Add example subtopics where appropriate."""
    topics = _topic_scope(
        topic_texts,
        scoped_template='only the topic(s) "{topic_texts}" each',
        default="each subtopic",
    )
    instruction = (
        f"Please add for {topics} a new subtopic 'examples' if not existent yet, "
        f"and add a new level with up to {TOP_MOST_RESULTS} top most important examples or extend the existing ones, "
        f"with each example {MAX_RETURN_WORDS} words at maximum. "
        "Do not change the central topic which is the top most topic. "
    )
    return _mermaid_prompt(instruction, text)


def prompt_news_to_mindmap(text: str, topic_texts: str = "") -> str:
    """Create a mindmap from trending topics based on the source mindmap."""
    del topic_texts
    instruction = (
        "What are the top 10 trending topics on Twitter and X about the given mindmap content? "
        "Please create a mindmap 6 levels deep from the trending topics including headlines and company names and using an incisive title of the words as central topic. "
        "For each topic generate a useful and sensible text without unnecessary abbreviations. "
    )
    return _mermaid_prompt(instruction, text)


def prompt_text_to_mindmap(text: str, topic_texts: str = "") -> str:
    """Convert freeform text to a mindmap using a provided central topic."""
    instruction = (
        f"Please create a mindmap from the summary using '{topic_texts}' as central topic, "
        f"add at least 2 levels with up to {TOP_MOST_RESULTS} top most important topics each. "
        "For each topic generate a useful and sensible text without unnecessary abbreviations. "
    )
    return _mermaid_prompt(instruction, text, prefix=prompt_prefix_text)


def prompt_pdfsimple_to_mindmap(text: str, topic_texts: str = "") -> str:
    """Extract text from uploaded PDF content and turn it into a mindmap."""
    del text  # data for this prompt is delivered via the multimodal payload
    instruction = (
        f"Extract the content from the file or files, thoroughly summarize it and create a mindmap from the summary using '{topic_texts}' as central topic, "
        f"with at least 5 first level topics and add at least 3 more levels with up to {TOP_MOST_RESULTS} top most important topics each. "
        "For each topic generate a useful and sensible text without unnecessary abbreviations. "
    )
    return f"{instruction}{prompt_postfix_without_data}"


def prompt_md_to_mindmap(text: str, topic_texts: str = "") -> str:
    """Convert markdown content to a Mermaid mindmap."""
    instruction = (
        "Given is the following markdown code. Please convert it to a 1:1 Mermaid mindmap. "
        "Don't cut off any topic or reduce the input in any way. "
        f"Use '{topic_texts}' as central topic, if there is no top most item. "
    )
    return _mermaid_prompt(instruction, text, prefix="")


def prompt_text_to_knowledgegraph(text: str, topic_texts: str = "") -> str:
    """Build a knowledge graph in Mermaid syntax from text."""
    del topic_texts
    instruction = (
        "Please create a knowledge graph from the following text and return it in valid Mermaid syntax. Don't add any additional text or explanations. "
    )
    return _mermaid_prompt(instruction, text, prefix="")


def prompt_knowledgegraph_to_mindmap(text: str, topic_texts: str = "") -> str:
    """Convert Mermaid graph data to a mindmap."""
    del topic_texts
    instruction = (
        "Please create a mindmap from the following mermaid graph data and return it in valid mermaid syntax. Don't add any additional text or explanations. "
    )
    return _mermaid_prompt(instruction, text, prefix="")


def prompts_list_from_param(param: str) -> list[str]:
    """Return an ordered list of prompt ids to execute for a given complexity."""
    if param == "complexity_1":
        return ["refine", "refine", "cluster"]
    if param == "complexity_2":
        return ["exp_prj_prc_org", "refine"]
    if param == "complexity_3":
        return ["prj_prc_org", "refine"]
    return [param]


def prompt(param: str, text: str, topic_texts: str = "", freetext: str = "") -> str:
    """Dispatch to a concrete prompt builder."""
    text_input = _normalize_text(text)
    prompt_functions = {
        "refine": prompt_refine,
        "refine_grounding": prompt_refine,
        "answer_grounding": prompt_answer,
        "refine_dev": prompt_refine_dev,
        "examples": prompt_examples,
        "cluster": prompt_cluster,
        "prc_org": prompt_prc_org,
        "prj_prc_org": prompt_prj_prc_org,
        "exp_prj_prc_org": prompt_exp_prj_prc_org,
        "exp": prompt_exp,
        "prj_org": prompt_prj_org,
        "capex_opex": prompt_capex_opex,
        "glossary": prompt_glossary,
        "argumentation": prompt_argumentation,
        "text2mindmap": prompt_text_to_mindmap,
        "pdfsimple2mindmap": prompt_pdfsimple_to_mindmap,
        "md2mindmap": prompt_md_to_mindmap,
        "text2knowledgegraph": prompt_text_to_knowledgegraph,
        "knowledgegraph2mindmap": prompt_knowledgegraph_to_mindmap,
        "news": prompt_news_to_mindmap,
        "freetext": prompt_freetext,
    }

    prompt_function = prompt_functions.get(param)
    if prompt_function is None:
        return ""

    if prompt_function is prompt_freetext:
        return prompt_function(text_input, freetext=freetext, topic_texts=topic_texts)
    return prompt_function(text_input, topic_texts=topic_texts)
