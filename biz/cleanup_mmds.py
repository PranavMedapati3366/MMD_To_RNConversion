import os
import openai
import re
import json

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

json_file_path = '/Users/pranavreddy/Desktop/RNConvertion/output_jsons/mmd_chunk.json'
clean_up_json = "/Users/pranavreddy/Desktop/RNConvertion/output_jsons/mmd_clean_up.json"
cyc_cya_json = "/Users/pranavreddy/Desktop/RNConvertion/output_jsons/cyc_cya.json"
cleaned_mmd_output_folder_path = '/Users/pranavreddy/Desktop/RNConvertion/cleaned_mmd_chunks'  # Folder to save processed files

key = os.getenv("OPENAI_API_KEY")

# Helper function to split large sections into smaller parts
def split_large_text(text, max_length=7000):
    sentences = text.split('\n')
    parts, current_part = [], ""
    for sentence in sentences:
        if len(current_part) + len(sentence) + 1 < max_length:
            current_part += sentence + "\n"
        else:
            parts.append(current_part)
            current_part = sentence + "\n"
    parts.append(current_part)  # Add the last part
    return parts

def combine(results):
    cyc_map = {}
    for entry in results:
        if entry["type"] == "CYC":
            cyc_map[entry["meta"]] = {
                "title": entry["title"],
                "meta": entry["meta"],
                "cyc_file_path":entry["file_path"],
                "cya_file_path":"",
                "cyc_combined":"",
                "pos":entry["pos"],
                "filename":entry["filename"]
            }
        if entry["type"] == "CYA":
            if entry["meta"] in cyc_map:
                cyc_map[entry["meta"]]["cya_file"] = entry["title"]
                cyc_map[entry["meta"]]["cya_file_path"] = entry["file_path"]
            else:
                # In case CYA appears without CYC, still record it
                cyc_map[entry["meta"]] = {
                    "meta": entry["meta"],
                    "cya_file": entry["title"],
                    "cya_file_path":entry["file_path"],
                    "cyc_combined":"",
                    "pos":entry["pos"],
                    "filename":entry["filename"]
                }

    with open(cyc_cya_json, 'w') as f:
        json.dump(cyc_map, f, indent=2)
        print("file written success to cyc_cya.json")
    

array = []

def CleanUpChunkedmmd():
    
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    mmdListJson = data["chunks"]


    for mmdfileJson in mmdListJson:
        filename = mmdfileJson["filename"]
        if filename.endswith(".mmd"):  # Check for .mmd files
            file_path = mmdfileJson["file_path"]
            file_name_without_ext = os.path.splitext(os.path.basename(filename))[0]
            
            # Read content from file
            with open(file_path, 'r') as file:
                content = file.read()

            # Step 1: Split content into chunks based on sections
            sections = content.split(r'\section*')  # Keep everything, including the initial content
            chunks = [sections[0].strip()] + [f"\\section*{section.strip()}" for section in sections[1:]]

            # Prepare to collect all processed content for this file
            processed_content_list = []

            # Create a subfolder for the current file once (before processing chunks)
            os.makedirs(cleaned_mmd_output_folder_path, exist_ok=True)  # Create folder if it doesn't exist

            cleaned_output_file_path = ""

            # Process each chunk and prepare API requests
            for i, chunk in enumerate(chunks):
                print(f"index",i)

                # Split the chunk if it's too large
                sub_chunks = split_large_text(chunk)
                
                # Prepare to collect all processed sub-chunks for the current chunk
                chunk_processed_content = []

                for j, sub_chunk in enumerate(sub_chunks):
                    # Define a ChatGPT prompt
                    prompt = r"""
    Process the following markdown text carefully according to the rules below, ensuring precise and consistent formatting:
    0. Do not add any extra content, explanations, or AI-generated text beyond the specified modifications.
    1. Convert Tables to Pipe-Separated Format:
    - Identify all tables in the markdown and convert them to a pipe-separated format, using the pipe symbol (`|`) to separate each column.
    - Ensure each row and column is aligned correctly with the pipe symbol for readability.
    2. Format Inline Equations:
    - Locate all inline equations marked by `\(` and `\)`.
    - Replace `\(` and `\)` with `$` symbols at the beginning and end of each equation, using LaTeX syntax for inline math.
    3. Format Display Equations:
    - Identify all display equations marked by `\[` and `\]`.
    - Replace `\[` and `\]` with `$$` symbols at the beginning and end of each equation, using LaTeX syntax for display math.
    - Place each display equation on a new line, starting and ending with `$$`.
    4. Separate Multiple Equations on a Single Line:
    - If two or more equations are on the same line, format each one individually according to whether they are inline or display equations.
    - Place each equation on a separate line if there are multiple equations, maintaining clarity and uniformity.
    5. Process Every Line Thoroughly:
    - Go through each line of the markdown text without skipping any content.
    - Do not add any extra content, explanations, or AI-generated text beyond the specified modifications.
    - Apply each change exactly as directed across the entire document.
    Here is the markdown text to process:
                """ + sub_chunk

                    # Call OpenAI API with the processed content
                    response = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant for LaTeX and Markdown processing."},
                            {"role": "user", "content": prompt}
                        ],
                        api_key=key
                    )
                    # Extract the processed content
                    processed_content = response.choices[0].message['content']
                    processed_content = processed_content.replace("```markdown", "").replace("```", "")
                    # Post-process to ensure \[ \] are converted to $$ and \( \) are converted to $
                    processed_content = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", processed_content, flags=re.DOTALL)
                    processed_content = re.sub(r"\\\((.*?)\\\)", r"$\1$", processed_content, flags=re.DOTALL)

                    # Append the processed content for the current sub-chunk
                    chunk_processed_content.append(processed_content)

                # Save the processed content to a single file in the folder for the current file
                cleaned_output_file_path = os.path.join(cleaned_mmd_output_folder_path, f"{file_name_without_ext}_cleanedfile_chunk.mmd")
            
                with open(cleaned_output_file_path, 'w') as output_file:
                    output_file.write("\n\n".join(chunk_processed_content))  # Write all processed content for the current file
                print(f"Content saved to {cleaned_output_file_path}")
            
            array.append({
                "pos": mmdfileJson["pos"],
                "title": mmdfileJson["title"],
                "filename": mmdfileJson["filename"],
                "file_path": cleaned_output_file_path,
                "type": mmdfileJson["type"],
                "meta": mmdfileJson["meta"]
            })

    print("Processing complete.")
    with open(clean_up_json, 'w') as f:
        json.dump(array, f, indent=2)
        print("file written success mmd_clean_up.json")

    combine(array)

#CleanUpChunkedmmd()
