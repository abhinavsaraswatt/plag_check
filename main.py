import re


with open('temp.txt', 'r', encoding='utf-8') as file:
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

# Example usage
# text = "This is an example text where we want to split the content into lines that have a maximum of thirty words per line, ensuring the text is easier to read and process."
content = preprocess_text(content)
lines = split_text_by_dot(content, max_words=30)

i = 0
for line in lines:
    i += 1
    print(i, line)
# print("\n".join(lines))  # Print the split lines


