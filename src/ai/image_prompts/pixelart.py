# Title: Pixelart

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
        return (
            f"Generate an image of isometric perspective, detailed pixel art{(", " + style + ",") if style else ""} "
            f"from {"the core topics of this markdown" if subtopics == "" else "'" + subtopics + "' and the following markdown as context"}: "
            f"\n```markdown\n{context}```\n "
        )

def main():
    _prompt = MPrompt()
    prompt_text = _prompt.get_prompt(context='# Title\n  ## Main Topic\n    ### SubTopic 1\n      ### SubTopic 1.1\n      ### SubTopic 1.2\n')
    print(prompt_text)

if __name__ == "__main__":
    main()
