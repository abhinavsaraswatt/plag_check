import os

def split_text_by_last_dot(input_file, output_dir, max_words=1000):
    """
    Splits a text file into smaller files, each containing no more than `max_words`,
    ensuring the split happens at the last dot (.) before the limit.
    
    Args:
    - input_file (str): Path to the input file containing the text.
    - output_dir (str): Directory to save the output files.
    - max_words (int): Maximum number of words per file. Default is 1000.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Split the text into words
    words = text.split()
    file_index = 1  # Track the file numbering
    start_index = 0  # Start of the current chunk
    
    while start_index < len(words):
        end_index = min(start_index + max_words, len(words))  # Provisional end index
        chunk = words[start_index:end_index]  # Get the provisional chunk
        
        # Look for the last dot in the current chunk
        last_dot_index = -1
        for i, word in enumerate(chunk):
            if word.endswith('.'):
                last_dot_index = i
        
        # If a dot was found, limit to that index; otherwise, use the provisional chunk
        if last_dot_index != -1:
            chunk = words[start_index:start_index + last_dot_index + 1]
        
        # Convert chunk back to text
        chunk_text = ' '.join(chunk)
        
        # Create a filename for the chunk
        output_file = os.path.join(output_dir, f'chunk_{file_index}.txt')
        
        # Write the chunk to a new file
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write(chunk_text)
        
        print(f"Created {output_file}")
        file_index += 1
        start_index += len(chunk)  # Move to the next chunk

# Example usage
input_file = 'large_text.txt'  # Replace with your input file path
output_dir = 'output_chunks'   # Directory to save the output files

split_text_by_last_dot(input_file, output_dir, max_words=1000)
