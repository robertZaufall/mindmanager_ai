import tiktoken
import markdown_it
import re

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

def cleanse_markdown(markdown_text):
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
    return '\n'.join(cleaned_lines)

def ultra_minimize_tokens(text):
    abbrevs = {
        'information': 'info', 'example': 'eg', 'without': 'wo', 'with': 'w/',
        'about': 'abt', 'between': 'btw', 'number': '#', 'please': 'pls',
        'people': 'ppl', 'because': 'bc', 'before': 'b4', 'software': 'sw',
        'hardware': 'hw', 'language': 'lang', 'zero': '0', 'one': '1', 'two': '2',
        'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7',
        'eight': '8', 'nine': '9', 'ten': '10', 'through': 'thru', 'okay': 'ok',
        'thanks': 'thx', 'government': 'govt', 'management': 'mgmt',
        'development': 'dev', 'international': 'intl', 'technology': 'tech',
        'something': 'sth', 'someone': 'sm1', 'everybody': 'evrybdy',
        'everyone': 'evryone', 'everything': 'evrythng', 'tomorrow': 'tmrw',
        'tonight': '2nite', 'today': '2day', 'yesterday': 'ystday',
        'application': 'app', 'applications': 'apps', 'appointment': 'appt',
        'appointments': 'appts', 'message': 'msg', 'messages': 'msgs',
        'question': 'q', 'questions': 'qs', 'answer': 'a', 'answers': 'as',
        'document': 'doc', 'documents': 'docs', 'advertisement': 'ad',
        'advertisements': 'ads', 'account': 'acct', 'accounts': 'accts',
        'address': 'addr', 'addresses': 'addrs', 'administrator': 'admin',
        'administrators': 'admins', 'approximately': 'approx', 'assignment': 'assgmt', 
        'assignments': 'assgmts', 'attention': 'attn', 'avenue': 'ave', 'average': 'avg'
    }
    
    verb_synonyms = {
        'facilitate': 'help', 'investigate': 'study', 'utilize': 'use',
        'implement': 'do', 'demonstrate': 'show', 'communicate': 'talk',
        'collaborate': 'work', 'evaluate': 'check', 'generate': 'make',
        'optimize': 'fix', 'analyze': 'study', 'establish': 'set',
        'consider': 'think', 'determine': 'find', 'enhance': 'boost',
        'provide': 'give', 'require': 'need', 'maintain': 'keep',
        'indicate': 'show', 'accomplish': 'do', 'acquire': 'get',
        'attempt': 'try', 'commence': 'start', 'complete': 'finish',
        'comprise': 'form', 'construct': 'build', 'decrease': 'cut',
        'designate': 'name', 'discontinue': 'stop', 'eliminate': 'cut',
        'emphasize': 'stress', 'encounter': 'meet', 'endeavor': 'try',
        'enumerate': 'list', 'exclude': 'bar', 'expedite': 'rush',
        'initiate': 'start', 'terminate': 'end', 'transmit': 'send'
    }

    other_synonyms = {
        'additional': 'more', 'alternatively': 'or', 'approximately': 'about',
        'assistance': 'help', 'component': 'part', 'components': 'parts',
        'concerning': 'about', 'consequently': 'so', 'currently': 'now',
        'equitable': 'fair', 'evidenced': 'shown', 'furthermore': 'also',
        'sufficient': 'enough', 'therefore': 'so'
    }

    contractions = {
        "n't": "'t", "'re": "'r", "'ve": "'v", "'ll": "'l", "'m": "'m", "'s": "'s"
    }
    
    stop_words = set(['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
                      'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
                      'to', 'was', 'were', 'will', 'with', 'very', 'your'])

    def conjugate_verb(verb, tense):
        if tense == 'present':
            return verb + 's' if verb[-1] != 's' else verb
        elif tense == 'past':
            if verb[-1] == 'e':
                return verb + 'd'
            elif verb[-1] == 'y' and verb[-2] not in 'aeiou':
                return verb[:-1] + 'ied'
            else:
                return verb + 'ed'
        elif tense == 'present_participle':
            if verb[-1] == 'e':
                return verb[:-1] + 'ing'
            else:
                return verb + 'ing'
        return verb

    # Generate all verb forms for synonyms
    all_synonyms = {}
    for verb, synonym in verb_synonyms.items():
        all_synonyms[verb] = synonym
        all_synonyms[conjugate_verb(verb, 'present')] = conjugate_verb(synonym, 'present')
        all_synonyms[conjugate_verb(verb, 'past')] = conjugate_verb(synonym, 'past')
        all_synonyms[conjugate_verb(verb, 'present_participle')] = conjugate_verb(synonym, 'present_participle')
    
    all_synonyms.update(other_synonyms)

    # Remove markdown elements and URLs
    text = re.sub(r'```[\s\S]*?```|\|.*\||!\[.*?\]\(.*?\)|http\S+|[#*`>]', '', text.lower())
    
    # Apply abbreviations, contractions, and synonyms
    for word, replacement in {**abbrevs, **contractions, **all_synonyms}.items():
        text = re.sub(r'\b' + word + r'\b', replacement, text)
    
    # Split into words, keeping periods, commas, and decimal numbers
    words = re.findall(r'\b\w+(?:\.\d+)?\b|[.,]', text)
    
    # Remove stop words, keep periods and commas, and join with correct spacing
    result = ''
    for i, w in enumerate(words):
        if w not in stop_words or w in '.,':
            if w in '.,':
                result = result.rstrip() + w + ' '
            elif '.' in w and w[0].isdigit() and w[-1].isdigit():  # Handle decimal numbers
                result += w + ' '
            elif i > 0 and words[i-1].isdigit() and w.isdigit():  # Handle cases like "gpt 3.5"
                result = result.rstrip() + '.' + w + ' '
            else:
                result += w + ' '
    
    return result.strip()