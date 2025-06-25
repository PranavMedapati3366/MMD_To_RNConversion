

import os
import json
import copy
import requests
import time

# Global URL and TOKEN
BULK_API_URL = "https://bff.allen-stage.in/internal-bff/api/v1/learningMaterials/bulk_create"

UPLOAD_RAW_DATA_URL = "https://bff.allen-stage.in/lmm/uploadRawData"

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhVVNzVzhHSTAzZHlRMEFJRlZuOTIiLCJkX3R5cGUiOiJ3ZWIiLCJkaWQiOiJiZjEyMDg0OC0yNDNlLTRjOGYtOTQ2OC00OTFjMWIwNWVmNjEiLCJlX2lkIjoiMjk2OTg4NjgzIiwiZXhwIjoxNzUwODM2OTQyLCJpYXQiOiIyMDI1LTA2LTI1VDA2OjM1OjQyLjM0ODQxNTkxN1oiLCJpc3MiOiJhdXRoZW50aWNhdGlvbi5hbGxlbi1zdGFnZSIsImlzdSI6IiIsInB0IjoiVEVBQ0hFUiIsInNpZCI6ImM3OGFjYzk5LTg4NzUtNGMyOC1hNDgwLTZmN2U0MGYyOWIyMCIsInRpZCI6ImFVU3NXOEdJMDNkeVEwQUlGVm45MiIsInR5cGUiOiJhY2Nlc3MiLCJ1aWQiOiJjTkc4TmpIbW9pNkVTNGFQQ1RJQVIifQ.bwlIUDs5ic9-jjpJvjLdu9DWScI2N7p8nlFnlmco5gM"

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {TOKEN}'
}


ordered_content_ids = []

bulk_create_request_template = {
    "requests": [
        {
            "learning_material": {
                "language": "ENGLISH",
                "client_id": "Console",
                "tenant_id": "ALLEN",
                "session": "2024-2025",
                "center_id": "facility_j1IwGFcbbdl3LSALAsGIX",
                "taxonomy_center": "ADPL",
                "learning_category": "SELF_PACED",
                "taxonomies": [
                    {
                        "taxonomy_Id": "1699105259uJ",
                        "node_id": "809"
                    }
                ],
                "content_stakeholders": {
                    "faculty_name": "",
                    "faculty_emp_id": "",
                    "faculty_user_id": "",
                    "created_by": " "
                },
                "id": "",
                "name": "",
                "description": "",
                "hashtags": [],
                "duration_minutes": 0,
                "type": "ASSET_LIBRARY",
                "sub_type": "TEXT",
                "review_details": {
                    "reviewed_by": "",
                    "reviewed_on": 0,
                    "comments": ""
                },
                "material_tags":{}
            },
            "filename": "",
            "isPrivate": True
        }
    ]
}

def createRN(content_id_list):
    element_list = [{"id": cid} for cid in content_id_list]

    rn_structure = {
        "version": 1,
        "configData": {
            "elements": {},
            "scenes": [
                {
                    "elementList": element_list
                }
            ]
        }
    }

    return json.dumps(rn_structure)

def createRawData(jsonStr):  #if text comes then this format should be there
    try:
        converted_json = json.loads(jsonStr)

        wrapped_json = {
            "format": "LEXICAL",
            "version": 1,
            "configData": converted_json
        }

        return json.dumps(wrapped_json)

    except json.JSONDecodeError as e:
        print(f"Error Ocuured in createRawData : ",e)
        return

def CreateAsset(data,source_id):
    request = copy.deepcopy(bulk_create_request_template)
    
    request["requests"][0]["filename"] = data["fileName"]
    request["requests"][0]["learning_material"]["name"] = data.get("name", data["fileName"])
    request["requests"][0]["learning_material"]["description"] = data.get("description", "Auto-generated asset")
    c_type = data["type"]
    request["requests"][0]["learning_material"]["sub_type"] = c_type
    request["requests"][0]["learning_material"]["material_tags"]={
        "source_id":source_id
    }

    request_json_str = json.dumps(request)
    
    bulkResponse = requests.post(BULK_API_URL, headers=HEADERS, data=request_json_str)   #bulk create
    
    print(f"Create Asset Status Code: ", bulkResponse.status_code)

    if (bulkResponse.status_code==200):

        bulkResponse = bulkResponse.json()
    
        c_id = bulkResponse["data"]["materials"][0]["id"]

        raw_data = ""
        if data["type"] == "QUESTION":
            converted_json = json.loads(data["jsonData"])
            raw_data = json.dumps(converted_json)
        else:
            raw_data = createRawData(data["jsonData"])

        next_payload = {
            "content_id": c_id,
            "content_type": "ORIGINAL",
            "raw_data": raw_data,
            "raw_data_type": "TEXT_ASSET",
            "content_meta": {}
        }

        print(next_payload)

        rawDataResponse = requests.post(UPLOAD_RAW_DATA_URL, headers=HEADERS, data=json.dumps(next_payload))
        if(rawDataResponse==""):
            return None


        print(rawDataResponse.json())
        ordered_content_ids.append(c_id)

        print("Asset is Created")
    else:
        print(f"failed status code for file {data["fileName"]} is : {bulkResponse.status_code}")
        return None



def CreateRevisionNotes(rn_rawData,originalFilePath,source_id):
    request = copy.deepcopy(bulk_create_request_template)

    request["requests"][0]["type"] = "REVISION_MATERIAL"
    request["requests"][0]["sub_type"] = "REVISION_NOTES"    
    request["requests"][0]["duration_minutes"] = 2

    request["requests"][0]["learning_material"]["material_tags"] = {
        "source_id":source_id
    }


    base_name = os.path.basename(originalFilePath)

    # Split the name and extension
    name_without_ext = os.path.splitext(base_name)[0]  # "a"

    # Add .json extension
    new_filename = name_without_ext + ".json"

    request["requests"][0]["filename"] = new_filename
    request["requests"][0]["learning_material"]["name"] = name_without_ext

    json_str = json.dumps(request)

    print(f"req for bulk api:",json_str)

    #print("Request JSON for bulk_create:\n", json_str)

    
    bulkResponse = requests.post(BULK_API_URL, headers=HEADERS, data=json_str)

    if(bulkResponse.status_code!=200):
        return

    response_data = bulkResponse.json()
    r_id = response_data["data"]["materials"][0]["id"]

    rawDataPayload = {
            "content_id": r_id,
            "content_type": "ORIGINAL",
            "raw_data": rn_rawData,
            "raw_data_type": "CAPSULE",
            "content_meta": {}
        }

    print("calling upload raw data RN .........")


    rawDataResponse = requests.post(UPLOAD_RAW_DATA_URL, headers=HEADERS, data=json.dumps(rawDataPayload))

    rawDataResponse = rawDataResponse.json()
    print(f"upload raw data response id is : {rawDataResponse["id"]}")
    return rawDataResponse["id"]

#-----------------Main Execution---------------------------

def RNExecution(original_file_path,source_id):
    try:
        file_path = "/Users/pranavreddy/Desktop/RNConvertion/output_jsons/final_list_output.json"
        print(file_path)
        print(source_id)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for jsonData in data:
            print("Waiting for 1 seconds...")
            time.sleep(1)
            print("Done waiting!")
            result = CreateAsset(jsonData,source_id)  # assign the return value



        rn_rawData = createRN(ordered_content_ids)
        rn_id = CreateRevisionNotes(rn_rawData,original_file_path,source_id)
        print(f"final rn_id is {rn_id}")
        return rn_id
    except: 
        print("Fsomething went wrong")


    print("\n✅ Ordered content IDs:")
    for cid in ordered_content_ids:
        print(cid)


#RNExecution("/Users/pranavreddy/Desktop/RNConvertion/inputs_files/Heredity1.mmd","abc123")