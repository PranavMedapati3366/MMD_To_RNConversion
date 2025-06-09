import os
import json


json_file_path = "/Users/pranavreddy/Desktop/RNConvertion/output_jsons/cyc_cya.json"
cyc_merge_output_folder = "/Users/pranavreddy/Desktop/RNConvertion/cyc_merge"


def chunk_mmd_file(input_file):
    # Open and read the content of the .mmd file
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content by '##' to create chunks
    chunks = content.split('##')

    # Optionally, remove any leading/trailing whitespaces from each chunk
    # Also remove empty chunks
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

    return chunks

def save_chunks_to_files(chunks, output_dir, file_name_without_extension,jsonData):
    # Create subfolder named after the original file (without the .mmd extension)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    subfolder_path = os.path.join(output_dir, file_name_without_extension)
    
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)

    queList = []

    # Save each chunk into a separate file inside the subfolder
    for i, chunk in enumerate(chunks):
        # Add one blank line after the question
        # Split the chunk into the question and answer
        parts = chunk.split('\n', 1)  # Split only at the first newline
        
        if len(parts) > 1:
            question = parts[0].strip()  # The question (first line)
            answer = parts[1].strip()  # The answer (remaining content)
        else:
            question = parts[0].strip()
            answer = ''
        
        # Combine the question and answer with a blank line after the question
        formatted_chunk = f"## {question}\n\n{answer}"

        # Output filename as Question{i + 1}.mmd
        output_file = os.path.join(subfolder_path, f"Question{i + 1}.mmd")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(formatted_chunk)
            print(f"Saved Question {i + 1} to {output_file}")
        queList.append({
            "title":f"Question{i + 1}",
            "file_path":output_file
        })
    jsonData["que_list"] = queList

def ChunkCYCAndCYA():
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    for jsonData in data:
        combined_file_path = jsonData["cyc_combined"]

        filename = jsonData["filename"]
        print(filename)

        chunks = chunk_mmd_file(combined_file_path)
    
        save_chunks_to_files(chunks, cyc_merge_output_folder, filename,jsonData)

        with open(json_file_path, 'w') as f:
            json.dump(data, f, indent=2)
            print("file written success")

#ChunkCYCAndCYA()
