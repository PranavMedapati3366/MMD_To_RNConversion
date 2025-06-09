import openai
import os
import json
import shutil

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

key = os.getenv("OPENAI_API_KEY")

json_file_path = '/Users/pranavreddy/Desktop/RNConvertion/output_jsons/cyc_cya.json'
cyc_merge_output_folder = "/Users/pranavreddy/Desktop/RNConvertion/cyc_merge"

# Function to process the mmd files and generate a single output

def process_files(input_files, output_folder,value,array):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Create the output folder if it doesn't exist
    
    combined_content = ""

    # Read and combine the content of all mmd files
    for file_path in input_files:
        # Ensure the file exists
        if not os.path.isfile(file_path):
            print(f"Error: {file_path} is not a valid file.")
            continue
        
        # Read the content of the mmd file
        with open(file_path, 'r', encoding='utf-8') as file:
            combined_content += file.read() + "\n\n"  # Adding a new line between file contents

    # Construct the prompt to send to OpenAI
    prompt = f"""
You are given a list of questions and their answers. Format them into Markdown where:
- Each question is preceded by '##' (Markdown H2 header).
- Each answer is on a separate line with no additional formatting.
- Do not include any sections or headings like 'Check your Concepts' or 'Check your Answers'.

Questions and Answers:
{combined_content}
"""

    # Make the API call to OpenAI (chat model)
    openai.api_key = key
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Or use gpt-4 if needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=500,
        n=1,
        stop=None,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Get the formatted markdown response
    formatted_markdown = response['choices'][0]['message']['content'].strip()

    # Create a combined filename based on the input file names
    combined_filename = "_".join([os.path.splitext(os.path.basename(file))[0] for file in input_files]) + ".mmd"
    
    # Define the output file path (one single output file with a combined name)
    conmbined_output_file = os.path.join(output_folder, combined_filename)

    # Save the formatted markdown output
    with open(conmbined_output_file, 'w', encoding='utf-8') as output:
        output.write(formatted_markdown)
    
    value["cyc_combined"] = conmbined_output_file
    array.append(value)
    
    print(f"Processed and saved: {conmbined_output_file}")

# Main function to run the script
def MergeCYCAndCYA():

    with open(json_file_path, 'r') as f:
        data = json.load(f)

    if not os.path.exists(cyc_merge_output_folder):
        os.makedirs(cyc_merge_output_folder)
        print(f"Created folder: {cyc_merge_output_folder}")
    else:
        print(f"Folder already exists: {cyc_merge_output_folder}")

    array = []
    for key,value in data.items():
        print(value["title"])

        input_files = [
            value["cyc_file_path"],
            value["cya_file_path"]
        ]

        process_files(input_files, cyc_merge_output_folder,value,array)

    with open(json_file_path, 'w') as f:
        json.dump(array, f, indent=2)
        print("file written success to cyc_cya.json")
        
# Run the main function
#MergeCYCAndCYA()