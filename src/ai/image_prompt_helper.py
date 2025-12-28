import json
import os
import re

try:
    import yaml
except ImportError:
    yaml = None


PROMPTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "awesome-ai-models", "image", "image_prompts.yaml")
)
_PROMPT_DATA_CACHE = None


def _load_prompt_file(path):
    with open(path, "r", encoding="utf-8") as file:
        if yaml:
            return yaml.safe_load(file)
        return json.load(file)


def load_prompt_data(refresh=False):
    global _PROMPT_DATA_CACHE
    if _PROMPT_DATA_CACHE is not None and not refresh:
        return _PROMPT_DATA_CACHE

    if not os.path.exists(PROMPTS_PATH):
        _PROMPT_DATA_CACHE = {"templates": {}, "prompts": {}}
        return _PROMPT_DATA_CACHE

    data = _load_prompt_file(PROMPTS_PATH) or {}
    templates = {}
    prompts = {}

    if isinstance(data, dict):
        prompt_groups = data.get("prompt-groups", data.get("prompt_groups", []))
        if isinstance(prompt_groups, list):
            for group in prompt_groups:
                if not isinstance(group, dict):
                    continue
                group_base = group.get("prompt_base") or group.get("base")
                group_template = group.get("prompt_template") or group.get("template")
                group_prompts = group.get("prompts", [])
                if not isinstance(group_prompts, list):
                    continue
                for entry in group_prompts:
                    if not isinstance(entry, dict):
                        continue
                    merged = dict(entry)
                    if group_template and "prompt_template" not in merged:
                        merged["prompt_template"] = group_template
                    if group_base and "prompt_base" not in merged:
                        merged["prompt_base"] = group_base
                    name = merged.get("name")
                    if name:
                        prompts[str(name)] = merged

        prompt_entries = data.get("prompts", [])
        if isinstance(prompt_entries, list):
            for entry in prompt_entries:
                if not isinstance(entry, dict):
                    continue
                name = entry.get("name")
                if name:
                    prompts[str(name)] = entry
        elif isinstance(prompt_entries, dict):
            for name, entry in prompt_entries.items():
                if name:
                    prompts[str(name)] = entry if isinstance(entry, dict) else {"prompt_template": entry}

    _PROMPT_DATA_CACHE = {"templates": templates, "prompts": prompts}
    return _PROMPT_DATA_CACHE


def get_prompt_display_map():
    data = load_prompt_data()
    return {name.replace("_", " ").title(): name for name in data["prompts"]}


def render_image_prompt(prompt_name, context="", top_most_topic="", subtopics="", style=""):
    data = load_prompt_data()
    prompts = data["prompts"]
    templates = data["templates"]

    if not prompts:
        raise Exception(f"Error: {PROMPTS_PATH} is missing or empty.")

    if not prompt_name:
        prompt_name = "generic"
    prompt = prompts.get(prompt_name)
    if not prompt:
        raise Exception(f"Error: Prompt template '{prompt_name}' not found in {PROMPTS_PATH}.")

    context, top_most_topic, subtopics, style = _normalize_inputs(
        context, top_most_topic, subtopics, style
    )

    direct_template = prompt.get("prompt_template") or prompt.get("prompt")
    if prompt_name == "generic":
        if not direct_template:
            raise Exception(f"Error: Prompt template '{prompt_name}' is empty in {PROMPTS_PATH}.")
        return _render_generic_template(direct_template, top_most_topic, subtopics, style)

    if direct_template:
        return _render_base_template(
            template=direct_template,
            prompt_base=prompt.get("prompt_base"),
            prompt=prompt,
            context=context,
            top_most_topic=top_most_topic,
            subtopics=subtopics,
            style=style,
        )

    base_name = prompt.get("prompt_base")
    base_template = templates.get(base_name or "")
    if not base_template:
        raise Exception(f"Error: Prompt base '{base_name}' not found in {PROMPTS_PATH}.")

    return _render_base_template(
        template=base_template,
        prompt_base=base_name,
        prompt=prompt,
        context=context,
        top_most_topic=top_most_topic,
        subtopics=subtopics,
        style=style,
    )


def _normalize_inputs(context, top_most_topic, subtopics, style):
    return (
        str(context).strip() if context is not None else "",
        str(top_most_topic).strip() if top_most_topic is not None else "",
        str(subtopics).strip() if subtopics is not None else "",
        str(style).strip() if style is not None else "",
    )


def _render_generic_template(template, top_most_topic, subtopics, style):
    if subtopics and "," not in subtopics and not top_most_topic:
        top_most_topic = subtopics
        subtopics = ""

    if not top_most_topic:
        top_most_topic = "the main idea"

    style_with_prefix = f" {style}" if style else ""
    subtopics_sentence = (
        f" Emphasize how '{subtopics}' supports the main idea." if subtopics else ""
    )

    working = template.strip()
    working = working.replace("<style-with-prefix>", style_with_prefix)
    working = working.replace("<top_most_topic>", top_most_topic)
    working = working.replace("<subtopics-sentence>", subtopics_sentence)
    working = _cleanup_template(working)
    return working.strip()


def _render_base_template(template, prompt_base, prompt, context, top_most_topic, subtopics, style):
    subject = _get_text(prompt, "subject")
    detail = _get_text(prompt, "detail")
    additional_info = _get_text(prompt, "additional_info")

    if not subject:
        raise Exception(f"Error: Missing subject for '{prompt.get('name', 'unknown')}'.")

    working = template.strip()
    if "<top_most_topic>" in working and not top_most_topic:
        working = working.replace("on or about <top_most_topic>", "")

    replacements = {
        "<subject>": subject,
        "<detail>": detail,
        "<additional-info>": additional_info,
        "<style-with-prefix>": f", {style}" if style else "",
        "<subtopics-with-prefix>": _build_subtopics_prefix(prompt_base, subtopics, context),
        "<context-with-prefix>": _build_context_prefix(context),
    }

    for token, value in replacements.items():
        working = working.replace(token, value)

    if "<top_most_topic>" in working:
        working = working.replace("<top_most_topic>", top_most_topic)

    working = _cleanup_template(working)

    if context:
        working = working.replace("<context>", context)

    return working.strip()


def _get_text(prompt, key):
    value = prompt.get(key, "") if isinstance(prompt, dict) else ""
    return str(value).strip() if value is not None else ""


def _build_subtopics_prefix(prompt_base, subtopics, context):
    if prompt_base == "template-create":
        if subtopics:
            return f" about '{subtopics}'"
        if context:
            return " about the core topics of this markdown"
        return ""

    if subtopics:
        return f" from '{subtopics}'"
    if context:
        return " from the core topics of this markdown"
    return " from the main idea"


def _build_context_prefix(context):
    if not context:
        return ""
    return " and the following markdown as context:\n```markdown\n<context>```"


def _cleanup_template(template):
    lines = []
    for line in template.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        cleaned = cleaned.replace(" ,", ",").replace(" .", ".").replace(" :", ":")
        cleaned = re.sub(r",\s*,+", ",", cleaned)
        if cleaned:
            lines.append(cleaned)
    return "\n".join(lines)
