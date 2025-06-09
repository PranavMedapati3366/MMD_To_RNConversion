import subprocess
from .generate_mmds import GetChunkedmmds
from .cleanup_mmds import CleanUpChunkedmmd
from .cyc_cya_merge import MergeCYCAndCYA
from .cyc_cya_chunk import ChunkCYCAndCYA
from .revision_notes_converter import RNExecution
#from .pdf_to_mmd1 import GetMMDFromPdf

import shutil
import os
import csv

def delete_folder_if_exists(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"Folder does not exist: {folder_path}")


def write_to_csv(c_id, rn_id, csv_path='content_revision_map.csv'):
    file_exists = os.path.isfile(csv_path)

    with open(csv_path, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["pdf_content_id", "revision_notes_id"])

        # Write header only if file does not exist
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "pdf_content_id": c_id,
            "revision_notes_id": rn_id
        })

    print(f"✅ Written to CSV: {csv_path}")


def StartExecution(content_id):
    try:

        # input_mmd_file,original_pdf_file = GetMMDFromPdf(content_id)
        input_mmd_file = "/Users/pranavreddy/Desktop/RNConvertion/inputs_files/Respiration.mmd"

        # GetChunkedmmds(input_mmd_file)
        # CleanUpChunkedmmd()
        # MergeCYCAndCYA()
        # ChunkCYCAndCYA()

        print("Running Asset.js...")
        subprocess.run(["node", "biz/asset.js", content_id], check=True)

        rn_content_id = RNExecution(input_mmd_file,content_id)

    except subprocess.CalledProcessError as e:
        print(f"Subprocess failed: {e}")
    except Exception as e:
        print(f"Execution failed: {e}")

    # delete_folder_if_exists("/Users/pranavreddy/Downloads/Foundation/chunkedmmd")
    # delete_folder_if_exists("/Users/pranavreddy/Downloads/Foundation/cleaned_mmd_chunks")
    # delete_folder_if_exists("/Users/pranavreddy/Downloads/Foundation/pranav_codes/cyc_merge")
    # delete_folder_if_exists("/Users/pranavreddy/Downloads/Foundation/pranav_codes/CYCandCYA_stringified_output")

StartExecution("abc12345")
