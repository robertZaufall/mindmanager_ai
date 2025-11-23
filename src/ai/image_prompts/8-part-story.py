# Title: 8-Part Story

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
        return (
            "Create a beautifully entertaining 8 part story in one image with one blue character and his adventures. "
            "The story is thrilling throughout with emotional highs and lows and ending on a "
            "great twist and high note. Do not include any words or text on the images but tell the story purely through the imagery itself. "
            f"Take this mindmap in mermaid syntax as context: \n```\n{context}```\n "
        )

def main():
    _prompt = MPrompt()
    prompt_text = _prompt.get_prompt(context='mindmap\n  Main Topic\n    Topic 1\n      Topic 1.1\n      Topic 1.2\n')
    print(prompt_text)

if __name__ == "__main__":
    main()
