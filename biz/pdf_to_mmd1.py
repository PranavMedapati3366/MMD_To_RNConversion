import os
import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhVVNzVzhHSTAzZHlRMEFJRlZuOTIiLCJkX3R5cGUiOiJ3ZWIiLCJkaWQiOiJiZjEyMDg0OC0yNDNlLTRjOGYtOTQ2OC00OTFjMWIwNWVmNjEiLCJlX2lkIjoiMjk2OTg4NjgzIiwiZXhwIjoxNzQ4OTQyNjIyLCJpYXQiOiIyMDI1LTA2LTAzVDA4OjIzOjQyLjgyNzE4NzM1MloiLCJpc3MiOiJhdXRoZW50aWNhdGlvbi5hbGxlbi1zdGFnZSIsImlzdSI6IiIsInB0IjoiVEVBQ0hFUiIsInNpZCI6IjM3YTc4MjhlLWYwODktNDk3OS1hNTY4LThjN2Y5NjdkNmY4OSIsInRpZCI6ImFVU3NXOEdJMDNkeVEwQUlGVm45MiIsInR5cGUiOiJhY2Nlc3MiLCJ1aWQiOiJjTkc4TmpIbW9pNkVTNGFQQ1RJQVIifQ.nyyAqR0QNWD9LrRARGHkntq_NbGMK8glWkpR8k3lzSE",  # shortened
    "Content-Type": "application/json"
}

def download_pdf(url, content_file_name):
    input_dir = "/Users/pranavreddy/Desktop/RNConvertion/inputs_files"
    os.makedirs(input_dir, exist_ok=True)

    save_path = os.path.join(input_dir, f"{content_file_name}.pdf")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"PDF downloaded to: {save_path}")
        return save_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return None

def fetch_material_info(content_id):
    url = 'https://bff.allen-stage.in/lmm/MaterialInfoWithFileContentBulk'

    body = {
        "ids": [content_id],
        "include_raw_data": False,
        "include_secondary_content": False
    }

    try:
        response = requests.post(url, json=body, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data["data"][content_id]["error"] != "":
                print("Error occurred")
                return None, None

            content_file_name = data["data"][content_id]["material_info"]["name"]
            presigned_url = data["data"][content_id]["original_file_content"]["presigned_url"]
            print(f"File name: {content_file_name}")
            return presigned_url, content_file_name

        else:
            print(f"Failed with status: {response.status_code}")
            return None, None

    except Exception as e:
        print(f"Failed to fetch material info: {e}")
        return None, None

def process_pdf(pdf_file):

    url = 'https://api.mathpix.com/v3/pdf'
    headers = {
        'app_id': 'webtech_allen_ac_in_b6eda4_55dc4b',
        'app_key': 'a869e65df7d85c35385bcc8ca72f8c83a5423865f702df7d56e52cf8366d1113'
    }
    files = {
        'file': open(pdf_file, 'rb')
    }
    data = {
        'options_json': '{"rm_spaces": true, "metadata": {"improve_mathpix": false}, "auto_number_sections": false, "remove_section_numbering": false, "preserve_section_numbering": true}'
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    response_data = response.json()
    pdf_id = response_data.get('pdf_id')
    url = f'https://api.mathpix.com/v3/pdf/{pdf_id}'
    status = None
    while status != "completed":
        print(status)
        response = requests.get(url, headers=headers)
        response_data = response.json()
        status = response_data.get('status')
    output_location = os.path.join(os.path.dirname(pdf_file), f"{os.path.splitext(os.path.basename(pdf_file))[0]}.mmd")
    url = f'https://api.mathpix.com/v3/pdf/{pdf_id}.mmd'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(output_location, 'wb') as f:
            f.write(response.content)
        print("Data saved successfully to:", output_location)
        return output_location
    else:
        print("Error:", response.text)

#MAIN FUNC 

def GetMMDFromPdf(content_id):
    # url, file_name = fetch_material_info(content_id)
    # print(f"file name is ",file_name)
    # if url and file_name:
    #     pdf_file = download_pdf(url, file_name)

    pdf_file = "/Users/pranavreddy/Desktop/RNConvertion/inputs_files/Nutrition.pdf"
    
    output_mmd_path = process_pdf(pdf_file)

    return output_mmd_path,pdf_file


