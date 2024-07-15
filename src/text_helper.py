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