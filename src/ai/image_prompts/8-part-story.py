# Title: 8-Part Story

class MPrompt:
    _cloud_type: str = ""

    def __init__(self, cloud_type: str=""):
        self._cloud_type = cloud_type

    def get_prompt(self, 
            context: str="",
            top_most_topic: str="", 
            subtopics: str="",
            style: str="",
        ) -> str:
        result = f"Create a beautifully entertaining 8 part story{(' on ' + top_most_topic) if top_most_topic else ''} in one image with one blue character and his adventures"
        if context:
            result += f" about {"the core topics of this markdown" if subtopics == "" else "'" + subtopics + "' and the following markdown as context"}:\n```markdown\n{context}```\n"
        else:
            result += f"{ "." if subtopics == "" else " about '" + subtopics + "'."}\n"
        result += (
            "The story is thrilling throughout with emotional highs and lows and ending on a "
            "great twist and high note. Do not include any words or text on the images but tell the story purely through the imagery itself. "
        )
        return result

def main():
    _prompt = MPrompt()
    print(_prompt.get_prompt(top_most_topic="Main Topic", subtopics="SubTopic 1, SubTopic 2", context=''))
    print(_prompt.get_prompt(top_most_topic="Main Topic", subtopics="", context='# Title\n  ## Main Topic\n    ### SubTopic 1\n      ### SubTopic 1.1\n      ### SubTopic 1.2\n'))

    print(_prompt.get_prompt(top_most_topic="Main Topic", subtopics="SubTopic 1, SubTopic 2", context='# Title\n  ## Main Topic\n    ### SubTopic 1\n      ### SubTopic 1.1\n      ### SubTopic 1.2\n'))
    print(_prompt.get_prompt(top_most_topic="", subtopics="", context='# Title\n  ## Main Topic\n    ### SubTopic 1\n      ### SubTopic 1.1\n      ### SubTopic 1.2\n'))

if __name__ == "__main__":
    main()
