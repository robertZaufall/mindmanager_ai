class MPrompt:
    _cloud_type: str = ""
    _explicit_style: str = ""

    def __init__(self, cloud_type: str="", _explicit_style: str=""):
        self._cloud_type = cloud_type
        self._explicit_style = _explicit_style

    def get_prompt(self,
            context: str="",
            top_most_topic: str="", 
            subtopics: str="" 
        ) -> str:

        # Fallback for Nano Banana
        if subtopics == "" and ("+gemini-3-pro-image" in self._cloud_type or "+gemini-2.5-flash-image" in self._cloud_type):
            import os, file_helper
            module = file_helper.load_module_from_path(os.path.join(os.path.dirname(__file__), 'infographic-business.py'), "mprompt")
            mprompt = module.MPrompt(self._cloud_type, self._explicit_style)
            return mprompt.get_prompt(context=context, top_most_topic=top_most_topic, subtopics=subtopics)
        
        prefix = f"Business graphic, minimalistic, professional {self._explicit_style}"
        postfix = "on a gray gradient background, visually appealing, expensive look, no text."
        topics = f" and also influenced by thought on {subtopics}" if subtopics else ""

        if "," not in subtopics and subtopics != "":
            top_most_topic = subtopics
            subtopics = ""

        if subtopics == "" and "," not in top_most_topic:
            result = f"{prefix} showing a strong scene representing {{{top_most_topic}}}, {postfix}"
        else:
            result = f"{prefix} stuffed with typical big symbols or a strong scene representing '{top_most_topic}'{topics}, {postfix}"
        return result

def main():
    _prompt = MPrompt()
    prompt_text = _prompt.get_prompt(top_most_topic='Main Topic', subtopics='Topic 1, Topic 2')
    print(prompt_text)

if __name__ == "__main__":
    main()
