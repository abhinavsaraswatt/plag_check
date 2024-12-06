import re

import requests
from bs4 import BeautifulSoup
from googlesearch import search
from difflib import SequenceMatcher

with open('temp_short.txt', 'r', encoding='utf-8') as file:
    content = file.read()

def preprocess_text(text):
    # Add a space after a dot if it's directly followed by a number or text without a space
    return re.sub(r'(\.)(\S)', r'\1 \2', text)

def split_text_by_dot(text, max_words=30):
    words = text.split()  # Split the text into individual words
    lines = []  # List to store the split text
    current_line = []  # Temporary storage for the current line's words

    for word in words:
        current_line.append(word)

        # If the current line reaches max_words
        if len(current_line) == max_words:
            # Check if the last word ends with a dot
            if current_line[-1].endswith('.'):
                lines.append(' '.join(current_line))
                current_line = []
            else:
                # Find the last word with a dot in the current_line
                last_dot_index = -1
                for i in range(len(current_line)):
                    if current_line[i].endswith('.'):
                        last_dot_index = i
                
                if last_dot_index != -1:  # If there's a word with a dot
                    lines.append(' '.join(current_line[:last_dot_index + 1]))
                    current_line = current_line[last_dot_index + 1:]  # Retain leftover words
                else:
                    # If no dot is found, keep the line as it is
                    lines.append(' '.join(current_line))
                    current_line = []

    # Append any remaining words as the final line
    if current_line:
        lines.append(' '.join(current_line))

    return lines




def fetch_content(url):
    """Fetch content of a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract visible text
        return ' '.join(soup.stripped_strings)
    except Exception as e:
        print(f"Error fetching {url}: {e}\n\n\n")
        return ""

def calculate_word_match_percentage(line, content):
    """Calculate the percentage of line's words found in the content."""
    line_words = set(line.lower().split())  # Words in the line
    content_words = set(content.lower().split())  # Words in the content
    
    matching_words = line_words.intersection(content_words)  # Words in both
    match_percentage = (len(matching_words) / len(line_words)) * 100  # Calculate percentage
    
    return match_percentage

def process_line_for_review(line, match_threshold=30):
    """Process a line to check if it should be reviewed based on matching words in content."""
    # Search the line on Google and get top 5 results
    print(f"---------------Searching for: {line}\n\n\n")
    search_results = list(search(line, num_results=5))
    
    for url in search_results:
        content = fetch_content(url)
        match_percentage = calculate_word_match_percentage(line, content)
        print(f"Similarity with {url}: {match_percentage:.2f}%\n\n\n")
        
        # If the match percentage is above the threshold, mark for manual review
        if match_percentage >= match_threshold:
            print(f"Line marked for manual review: {line}\n\n\n")
            return line  # Line marked for review
    
    return None  # No match found for review

# Example usage
# text = "This is an example text where we want to split the content into lines that have a maximum of thirty words per line, ensuring the text is easier to read and process."
content = preprocess_text(content)
lines = split_text_by_dot(content, max_words=30)

# i = 0
# for line in lines:
#     i += 1
#     print(i, line)
# print("\n".join(lines))  # Print the split lines

# # Example usage
# line = ("NCP senior leader Ajit Pawar parted from the NCP with some MLAs and took oath as the deputy Chief minister, "
#         "with many NCP leaders getting inducted into the cabinet.")

marked_lines = []
for line in lines:
    review_line = process_line_for_review(line)
    if review_line:
        marked_lines.append(review_line)

print("\nLines marked for manual review:\n\n\n")
for marked_line in marked_lines:
    print(marked_line)
