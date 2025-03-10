import tiktoken
import markdown_it
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import SnowballStemmer
import string
import heapq

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def remove_section(markdown_content, section_title):
    escaped_title = re.escape(section_title)
    pattern = rf'(?:^|\n)(?P<level>#{1,3}|\*\*)\s*{escaped_title}\s*(\*\*)?\n(.*?)(?=\n((?P=level)#|\*\*)|\Z)'
    cleaned_content = re.sub(pattern, '', markdown_content, flags=re.DOTALL | re.MULTILINE)
    cleaned_content = cleaned_content.rstrip() + '\n'
    return cleaned_content

def guess_language(text):
    sample_text = text[:1000].lower()
    tokens = word_tokenize(sample_text)
    supported_languages = {lang for lang in SnowballStemmer.languages if lang != "porter"}
    available_languages = [lang for lang in stopwords.fileids() if lang in supported_languages]
    stopword_counts = {}
    for lang in available_languages:
        sw = set(stopwords.words(lang))
        count = sum(1 for token in tokens if token in sw)
        stopword_counts[lang] = count
    max_count = max(stopword_counts.values(), default=0)
    candidate_languages = [lang for lang, count in stopword_counts.items() if count == max_count]
    if not candidate_languages:
        return "unknown"
    priority = [lang for lang in SnowballStemmer.languages if lang != "porter"]
    for lang in priority:
        if lang in candidate_languages:
            return lang
    return candidate_languages[0]

def nltk_summarize(text, language='english', reduction_ratio=0.5):
    sentences = sent_tokenize(text)
    if len(sentences) < 2:
        return text
    stop_words = set(stopwords.words(language))
    words = word_tokenize(text.lower())
    freq_table = {}
    for word in words:
        if word in stop_words or word in string.punctuation:
            continue
        freq_table[word] = freq_table.get(word, 0) + 1
    sentence_scores = {}
    for sentence in sentences:
        sentence_words = word_tokenize(sentence.lower())
        sentence_length = len(sentence_words)
        for word in sentence_words:
            if word in freq_table:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + freq_table[word]
        if sentence in sentence_scores and sentence_length > 0:
            sentence_scores[sentence] /= sentence_length
    num_sentences = max(1, int(len(sentences) * reduction_ratio))
    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary_sentences = [sentence for sentence in sentences if sentence in summary_sentences]
    return " ".join(summary_sentences)

def summarize_and_stem(text, language='english', reduction_ratio=0.5):
    summary = nltk_summarize(text, language, reduction_ratio)
    sentences = sent_tokenize(summary)
    stemmed_sentences = []
    for i, sentence in enumerate(sentences):
        tokens = word_tokenize(sentence)
        tokens = [token for token in tokens if token not in string.punctuation]
        stemmer = SnowballStemmer(language.lower())
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        stemmed_sentences.append(" ".join(stemmed_tokens))
    result = ". ".join([s.strip() for s in stemmed_sentences]) + "."
    return result.strip()

def cleanse_markdown(markdown_text, optimization_level = 1):
    def clean_line(line):
        # Remove special characters (except #, -, *, and .)
        line = re.sub(r'[^\w\s#\-*.]', '', line)
        
        # Convert to lowercase
        line = line.lower()
        
        # Remove common stop words (expand this list as needed)
        stop_words = set(['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but'])
        words = line.split()
        line = ' '.join([word for word in words if word not in stop_words])
        
        # Remove URLs
        line = re.sub(r'http\S+', '', line)
        
        # Remove extra spaces
        line = ' '.join(line.split())
        
        return line

    # Remove code blocks
    markdown_text = re.sub(r'```[\s\S]*?```', '', markdown_text)

    # Remove tables
    markdown_text = re.sub(r'\|.*\|', '', markdown_text)  # Remove table rows
    markdown_text = re.sub(r'^\s*[-:]+\s*\|', '', markdown_text, flags=re.MULTILINE)  # Remove table headers

    # Split the markdown into lines
    lines = markdown_text.split('\n')
    
    # Clean each line while preserving structure
    cleaned_lines = []
    for line in lines:
        if line.strip() and not line.strip().startswith('|'):  # Additional check to remove any remaining table lines
            cleaned_lines.append(clean_line(line))
    
    # Join the cleaned lines back together
    result = '\n'.join(cleaned_lines)

    if optimization_level > 1:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('punkt_tab')
        language = guess_language(result)
        result = summarize_and_stem(result, language=language, reduction_ratio=0.75)

    return result

def cleanse_title(text):
    return text.replace(".pdf", "").replace(".md", "").replace("_", " ").replace("-", " ")

def clean_result(input):
    result = input \
                .replace("```mermaid", "") \
                .replace("Here is the refined mindmap:\n\n", "") \
                .replace("Here is the refined mind map:\n\n", "") \
                .replace("Here is the refined mindmap data:", "") \
                .replace("Here is the refined mindmap in Mermaid syntax:", "") \
                .replace("Here is the refined mind map in Mermaid syntax:", "") \
                .replace("Here is the mindmap in Mermaid syntax based on the summary:", "") \
                .replace("mermaid mindmap\n", "") \
                .replace("mermaid\n", "") \
                .replace("2 space", "") \
                .replace("```", "") \
                .lstrip("\n") \
                .lstrip()
    
    lines = result.split("\n")
    if lines[0].startswith("  "):
        result = "\n".join(line[2:] for line in lines)
    return result.lstrip("\n").lstrip()
