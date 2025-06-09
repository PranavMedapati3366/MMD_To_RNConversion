import subprocess
from .generate_mmds import GetChunkedmmds
from .cleanup_mmds import CleanUpChunkedmmd
from .cyc_cya_merge import MergeCYCAndCYA
from .cyc_cya_chunk import ChunkCYCAndCYA
from .revision_notes_converter import RNExecution

import shutil
import os
import csv
import gdown

def delete_folder_if_exists(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"Folder does not exist: {folder_path}")


def write_to_csv(c_id, rn_id, csv_path='content_revision_notes_map.csv'):
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


def StartExecution(content_id,input_mmd_path):
    try:
        GetChunkedmmds(input_mmd_path)
        print("running cleanup.mmd ......")
        CleanUpChunkedmmd()
        print("running cyc cya merge mmd ......")
        MergeCYCAndCYA()
        print("running  chunk merge cyc")
        ChunkCYCAndCYA()

        print("Running Asset.js...")
        subprocess.run(["node", "biz/asset.js", content_id], check=True)

        rn_content_id = RNExecution(input_mmd_path,content_id)
        print(f"final rn ID is : {rn_content_id}")

        return rn_content_id

    except subprocess.CalledProcessError as e:
        print(f"Subprocess failed: {e}")
        return None
    except Exception as e:
        print(f"Execution failed: {e}")
        Return None

    delete_folder_if_exists("/Users/pranavreddy/Desktop/RNConvertion/output_mmds")
    delete_folder_if_exists("/Users/pranavreddy/Desktop/RNConvertion/cleaned_mmd_chunks")
    delete_folder_if_exists("/Users/pranavreddy/Desktop/RNConvertion/cyc_merge")
    delete_folder_if_exists("/Users/pranavreddy/Desktop/RNConvertion/image_assets")



# def download_mmd_from_gdrive(gdrive_url):
#     mmd_output_dir="/Users/pranavreddy/Desktop/RNConvertion/inputs_files"
#     if not os.path.exists(mmd_output_dir):
#         os.makedirs(mmd_output_dir)

#     try:
#         # Use gdown to download the file
#         downloaded_file = gdown.download(gdrive_url, output=None, quiet=False, fuzzy=True)

#         # Move the file to the output_dir if needed
#         if downloaded_file:
#             filename = os.path.basename(downloaded_file)
#             destination = os.path.join(mmd_output_dir, filename)
#             os.replace(downloaded_file, destination)
#             print(f"Downloaded: {destination}")
#             return destination
#         else:
#             print("Download failed.")
#             return None

#     except Exception as e:
#         print(f"Error downloading file: {e}")
#         return None



def ReadInputCSV(csv_file_path):

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            c_id = row["content_id"]
            input_mmd_path = row["mmd_file_path"]

            print(f"strated execution for id: {c_id} and path {input_mmd_path}")
            rn_id = StartExecution(c_id,input_mmd_path)

            write_to_csv(c_id,r_id)

ReadInputCSV("/Users/pranavreddy/Desktop/RNConvertion/RivisionNote_uploads - Sheet1.csv")
# StartExecution("test_cID","/Users/pranavreddy/Desktop/RNConvertion/inputs_files/Respiration.pdf")
