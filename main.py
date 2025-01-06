import re

import requests
from bs4 import BeautifulSoup
from googlesearch import search
from difflib import SequenceMatcher

from datetime import datetime


def initialize_html_report(file_path):
    """Initialize the HTML report with basic structure."""
    with open(file_path, "w", encoding="utf-8") as html_file:
        html_file.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Line Check Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        .line {{ margin-bottom: 20px; }}
        .marked {{ color: red; font-weight: bold; }}
        .timestamp {{ font-size: 0.9em; color: gray; }}
    </style>
</head>
<body>
    <h1>Line Check Results</h1>
    <p class="timestamp">Report initialized at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <div id="results">
""")

def append_to_html_report(file_path, percentage_matches, consecutive_matches):
    """Append all results to the HTML report."""
    with open(file_path, "w", encoding="utf-8") as html_file:
        html_file.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Matching Results</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .line { margin-bottom: 20px; }
                .matched { color: green; font-weight: bold; }
                .url { font-size: 14px; color: blue; }
                .remaining-urls { font-size: 14px; color: darkorange; }
            </style>
        </head>
        <body>
            <h1>Matching Results</h1>
            <h2>Percentage Matches</h2>
        """)

        i = 0
        for line, (words, url) in percentage_matches.items():
            i += 1
            html_file.write(f"""
            <div class="line">
                <p>{i}. <strong>Line:</strong> {line}</p>
                <p class="matched">Matching Words: <br>{', <br>'.join(words)}</p>
                <p class="url">Matched URL: <a href="{url}" target="_blank">{url}</a></p>
            </div>
            """)

        html_file.write("<h2>Consecutive Matches</h2>")
        #

        i = 0
        for line, (phrases, url, remaining_urls, matched_surrounding_lines_5, current_surrounding_lines_4) in consecutive_matches.items():

            matched_prev_line_2, matched_prev_line_1, matched_line, matched_next_line_1, matched_next_line_2 = matched_surrounding_lines_5

            current_prev_line_2, current_prev_line_1, current_next_line_1, current_next_line_2 = current_surrounding_lines_4

            i += 1
            html_file.write(f"""
            <div class="line">
                <p>{i}. <strong>Current Line:</strong> {line}</p>
                <p><strong>Current Line with Context:</strong>{current_prev_line_2} {current_prev_line_1} <strong>{line}</strong> {current_next_line_1} {current_next_line_2}</p>

                <p class="matched">Matched Phrases: <br>{', <br>'.join(phrases)}</p>
                <p class="url">Matched URL: <a href="{url}" target="_blank">{url}</a></p>
                <p class="url"><strong>Matched Line with Context:</strong> <br>{matched_prev_line_2} {matched_prev_line_1} <strong>{matched_line}</strong> {matched_next_line_1} {matched_next_line_2}</p>
            </div>
            """)

            
            if remaining_urls:
                html_file.write("<p class='remaining-urls'>Remaining URLs that were not checked:</p>")
                for remaining_url in remaining_urls:
                    html_file.write(f"<p class='remaining-urls'><a href='{remaining_url}' target='_blank'>{remaining_url}</a></p>")
            html_file.write("</div>")

        html_file.write("""
        </body>
        </html>
        """)


def finalize_html_report(file_path):
    """Finalize the HTML report by closing tags."""
    with open(file_path, "a", encoding="utf-8") as html_file:
        html_file.write("""
    </div>
</body>
</html>
""")


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

def check_consecutive_matches(line, content, threshold=4):
    """Check if there are 4 or more consecutive matching words."""
    line_words = line.lower().split()
    # content_words = content.lower().split()
    content_sentences = re.split(r'(?<=\.)', content.lower())  # Split content into sentences
    
    matched_consecutive = []
    # Initialize surrounding lines with None
    prev_line_2, prev_line_1, matched_line, next_line_1, next_line_2 = None, None, None, None, None
    
    # Check for consecutive word matches
    for i in range(len(line_words) - threshold + 1):
        phrase = ' '.join(line_words[i:i + threshold])
        if phrase in content.lower():
            matched_consecutive.append(phrase)
            
            for j, sentence in enumerate(content_sentences):
                if phrase in sentence:
                    # Grab two lines before and after
                    prev_line_2 = content_sentences[j - 2] if j - 2 >= 0 else None
                    prev_line_1 = content_sentences[j - 1] if j - 1 >= 0 else None
                    matched_line = sentence
                    next_line_1 = content_sentences[j + 1] if j + 1 < len(content_sentences) else None
                    next_line_2 = content_sentences[j + 2] if j + 2 < len(content_sentences) else None
    matched_surrouding_lines_5 = (prev_line_2, prev_line_1, matched_line, next_line_1, next_line_2)
    return matched_consecutive, matched_surrouding_lines_5


def fetch_content(url, retries=2, timeout=10):
    """Fetch content of a webpage with retry mechanism."""
    headers = {
    "Referer": "https://www.google.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1"
}
    for attempt in range(1, retries + 1):
        try:
            
            print(f"Attempt {attempt} to fetch: {url}")

            response = requests.get(
                url, 
                timeout=timeout, 
                headers=headers
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract visible text
            return ' '.join(soup.stripped_strings)
        except Exception as e:
            print(f"Error fetching {url} on attempt {attempt}: {e}")
            if attempt == retries:
                print("Max retries reached. Moving to next URL.")
                return ""



def calculate_word_match_percentage(line, content):
    """Calculate the percentage of line's words found in the content."""

    line_words = set(word for word in line.lower().split() if len(word) > 3)  # Words in the line
    content_words = set(word for word in content.lower().split() if len(word) > 3)  # Words in the content
    
    matching_words = line_words.intersection(content_words)  # Words in both
    try:
        match_percentage = (len(matching_words) / len(line_words)) * 100  # Calculate percentage
    except ZeroDivisionError:
        match_percentage = 0
    
    return match_percentage, matching_words 

def estimate_content_size(url):
    """Estimate the size of the content to be fetched from a URL."""
    try:
        # Make a HEAD request to get headers
        response = requests.head(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Accept": "*/*",
        })
        response.raise_for_status()

        # Extract content length from headers
        content_length = response.headers.get('Content-Length')
        if content_length:
            size_in_kb = int(content_length) / 1024  # Convert bytes to KB
            return f"{size_in_kb:.2f} KB"
        else:
            return "Size unknown (Content-Length not provided)"
    except Exception as e:
        print(f"Error estimating size for {url}: {e}")
        return "Error estimating size"


percentage_matches = {}
consecutive_matches = {}
def process_line_for_review(line, current_prev_line_2=None, current_prev_line_1=None, current_next_line_1=None, current_next_line_2=None, match_threshold=30):
    """Process a line to check if it should be reviewed based on matching words in content."""
    print(f"Searching for: {line}\n\n\n")
    search_results = list(search(line, num_results=5))
    matching_words = set()  # Initialize as an empty set to avoid UnboundLocalError
    matched_url_percentage = None
    matched_url_consecutive = None
    matched_consecutive = []
    remaining_urls = []  # Initialize to an empty list

    current_surrounding_lines_4 = (current_prev_line_2, current_prev_line_1, current_next_line_1, current_next_line_2)

    for idx, url in enumerate(search_results):
        try:
            # Check if the URL ends with a PDF extension
            if '.pdf' in url.lower():
                # Estimate size for PDF links
                estimated_size = estimate_content_size(url)
                print(f"Estimated size for {url}: {estimated_size}")

                # Prompt to confirm fetching if size is too large
                if "KB" in estimated_size and float(estimated_size.split()[0]) > 2048:  # Example threshold: 500 KB
                    proceed = input(f"Content size for {url} is large ({estimated_size}). Proceed? (y/n): ").strip().lower()
                    if proceed != 'y':
                        print(f"Skipping URL: {url}\n")
                        continue

            content = fetch_content(url)
            if current_place not in url or current_place == "":
                match_percentage, matching_words = calculate_word_match_percentage(line, content)
                print(f"Similarity with {url}: {match_percentage:.2f}%\nWords: {matching_words}\n\n\n")

                # Check percentage match
                if match_percentage >= match_threshold:
                    matched_url_percentage = url  # Save URL for percentage match
                    print(f"Line marked for percentage match review: {line}\n")
                    percentage_matches[line] = (matching_words, matched_url_percentage)

                # Check consecutive matches
                matched_consecutive, matched_surrounding_lines_5 = check_consecutive_matches(line, content)
                if matched_consecutive:
                    matched_url_consecutive = url  # Save URL for consecutive match
                    print(f"Consecutive match found: {', '.join(matched_consecutive)}\n")
                    remaining_urls = search_results[idx + 1:]
                    consecutive_matches[line] = (matched_consecutive, matched_url_consecutive, remaining_urls, matched_surrounding_lines_5, current_surrounding_lines_4)

                    break  # Stop further checking for consecutive matches after a match is found
        except KeyboardInterrupt:
            # Skip this URL if Ctrl+C is pressed
            print(f"Skipping URL: {url}\n")
            continue  # Move to the next URL
    return remaining_urls


file_name = f"output_chunks/{input('Write file name to check with extension: output_chunks/')}"
# file_name = 'large_text.txt'
# place from where we obtain content
current_place = input('Enter current website domain name (in form: abc.in): ')

with open(file_name, 'r', encoding='utf-8') as file:
    content = file.read()

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

# Initialize HTML report
html_file_path = f"{file_name}.html"
initialize_html_report(html_file_path)

for i, line in enumerate(lines):

    # Get the previous two lines, ensuring indices don't go below zero
    current_prev_line_2 = lines[i - 2] if i - 2 >= 0 else None
    current_prev_line_1 = lines[i - 1] if i - 1 >= 0 else None

    # Get the next two lines, ensuring indices don't exceed the length of the list
    current_next_line_1 = lines[i + 1] if i + 1 < len(lines) else None
    current_next_line_2 = lines[i + 2] if i + 2 < len(lines) else None

    print(f"Processing Line {i + 1}/{len(lines)}")  # Use i + 1 for human-readable indexing
    process_line_for_review(line, current_prev_line_2, current_prev_line_1, current_next_line_1, current_next_line_2)

    # After processing all lines, save results to the HTML report
    append_to_html_report(html_file_path, percentage_matches, consecutive_matches)



print(f"Results saved to {html_file_path}")