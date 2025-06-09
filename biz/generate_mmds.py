import os
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json
import shutil

json_output_folder = "/Users/pranavreddy/Desktop/RNConvertion/output_jsons"
mmd_chunk_json = '/Users/pranavreddy/Desktop/RNConvertion/output_jsons/mmd_chunk.json'
mmd_chunk_output_folder = "/Users/pranavreddy/Desktop/RNConvertion/output_mmds"

def extract(title): 
    cyc_string = "Check your Concepts"
    cya_string = "Check your Answers"
    cb_string = "Building Concepts"
    qt_string = "Quick Tips"
    isCYC = fuzz.ratio(title, cyc_string) > 80
    isCYA = fuzz.ratio(title, cya_string) > 80
    isCB = fuzz.ratio(title, cb_string) > 80
    isQT = fuzz.ratio(title, qt_string) > 80
    if (isCYC):
        match = re.search(r'(.+?)\s+(\d+)', title)
        return {"type": "CYC", "meta": match.group(2).strip()}
    if (isCYA):
        match = re.search(r'(.+?)\s+(\d+)', title)
        return {"type": "CYA", "meta": match.group(2).strip()}
    if (isCB):
        match = re.search(r'(.+?)\s+(\d+)', title)
        return {"type": "CB", "meta": match.group(2).strip()}
    if (isQT):
        return {"type": "SPECIAL", "meta": "0"}
    return {"type": "DEFAULT", "meta": "0"}

def chunk_mmd_by_section(input_file_path, mmd_chunk_output_folder_path):
    result = {
        "chunks": []
    }


    if not os.path.exists(mmd_chunk_output_folder_path):
        os.makedirs(mmd_chunk_output_folder_path)

    try:
        with open(input_file_path, 'r') as file:
            content = file.read()

        pattern = r'\\section\*\{(.*?)\}(.*?)(?=\\section\*\{|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)

        for idx, (title, section_content) in enumerate(matches, 1):
            section_filename = f"section_{idx}_{title}.mmd"
            section_filename = re.sub(r'[\\/*?:"<>|]', "_", section_filename)

            output_file_path = os.path.join(mmd_chunk_output_folder_path, section_filename)

            with open(output_file_path, 'w') as output_file:
                output_file.write(f"\\section*{{{title}}}\n\n{section_content.strip()}\n")

            meta = extract(title)
            chunkJson = {
                "pos": idx,
                "title": title,
                "filename": section_filename,
                "file_path":output_file_path,
                "type": meta["type"],
                "meta": meta["meta"]
            }

            result["chunks"].append(chunkJson)

        if not os.path.exists(json_output_folder):
            os.makedirs(json_output_folder)

        with open(mmd_chunk_json, 'w') as f:
            json.dump(result, f, indent=2)
            print("file written success mmd_chunk.json")
    
    except Exception as e:
        print(f"Error in chunk_mmd_by_section: {e}")

# ---- MAIN EXECUTION ----

def GetChunkedmmds(input_mmd_file):
    chunk_mmd_by_section(input_mmd_file, mmd_chunk_output_folder)



#GetChunkedmmds("/Users/pranavreddy/Desktop/RNConvertion/inputs_files/Respiration.mmd")