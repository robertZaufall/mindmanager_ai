class MPrompt:
    _cloud_type: str = ""
    _explicit_style: str = ""

    def __init__(self, cloud_type: str="", _explicit_style: str=""):
        self._cloud_type = cloud_type
        self._explicit_style = _explicit_style

    def get_prompt(self,
            context: str="",
            top_most_topic: str="", 
            subtopics: str="",
            style: str="", 
        ) -> str:

        main_topic = top_most_topic.strip()
        extra_topics = subtopics.strip()
        context = context.strip()
        style_hint = style.strip()

        if extra_topics and "," not in extra_topics and not main_topic:
            # Keep single-topic inputs predictable (old behavior fallback).
            main_topic = extra_topics
            extra_topics = ""

        extra_topic_list = [item.strip() for item in extra_topics.split(",") if item.strip()]
        explicit_style = f", {self._explicit_style}" if self._explicit_style else ""
        requested_style = f", {style_hint}" if style_hint else ""

        topic_clause = (
            f"a strong, business-focused scene illustrating the vision of {main_topic}"
        )

        subtopic_clause = ""
        if extra_topic_list:
            if len(extra_topic_list) == 1:
                subtopic_clause = f" Emphasize how '{extra_topic_list[0]}' supports the main idea."
            else:
                spotlight = ", ".join(extra_topic_list[:-1])
                subtopic_clause = (
                    f" Spotlight just symbols representing {spotlight} and {extra_topic_list[-1]} to show their relationship to the main idea."
                )

        context_clause = ""
        if context:
            context_clause = (
                " Ground the visual in the following business context so it conveys intent, stakeholders, and outcomes without text: "
                f"```markdown\n{context}\n```"
            )

        prompt = (
            "Business graphic, minimalistic, professional"
            f"{explicit_style}{requested_style}, "
            f"{topic_clause}.{subtopic_clause}"
            " On a gray gradient background with an expensive look, no text or labels."
            #f"{context_clause}"
        )
        return prompt.replace("  ", " ").strip()

def main():
    _prompt = MPrompt()
    prompt_text = _prompt.get_prompt(top_most_topic='Main Topic', subtopics='Topic 1, Topic 2')
    print(prompt_text)

if __name__ == "__main__":
    main()
