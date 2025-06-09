import https from 'https';
import fs from 'fs';
import * as fsPromise from 'fs/promises';
import path from 'path';
import url from 'url';

const token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhVVNzVzhHSTAzZHlRMEFJRlZuOTIiLCJkX3R5cGUiOiJ3ZWIiLCJkaWQiOiJiZjEyMDg0OC0yNDNlLTRjOGYtOTQ2OC00OTFjMWIwNWVmNjEiLCJlX2lkIjoiMjk2OTg4NjgzIiwiZXhwIjoxNzQ5MDM5MzU1LCJpYXQiOiIyMDI1LTA2LTA0VDExOjE1OjU1LjI5OTU0MjQ1M1oiLCJpc3MiOiJhdXRoZW50aWNhdGlvbi5hbGxlbi1zdGFnZSIsImlzdSI6IiIsInB0IjoiVEVBQ0hFUiIsInNpZCI6ImFiZTdiYjcwLTkyN2YtNDhmYy05NzAyLTJhNWRhZmVjMzRiOSIsInRpZCI6ImFVU3NXOEdJMDNkeVEwQUlGVm45MiIsInR5cGUiOiJhY2Nlc3MiLCJ1aWQiOiJjTkc4TmpIbW9pNkVTNGFQQ1RJQVIifQ.zJMt14IMfhyrUFr6XpLCescM4XXv1ZKccl8GX7KWQ10";
const image_asset_output_folder = "/Users/pranavreddy/Desktop/RNConvertion/image_assets"

const taxonomyPayloadTemplate = {
    learning_material: {
      language: "ENGLISH",
      client_id: "Console",
      tenant_id: "ALLEN",
      session: "2024-2025",
      center_id: "facility_j1IwGFcbbdl3LSALAsGIX",
      taxonomy_center: "ADPL",
      learning_category: "SELF_PACED",
      taxonomies: [
        {
          taxonomy_Id: "1701187953vC",
          node_id: "809"
        }
      ],
      content_stakeholders: {
        faculty_name: "",
        faculty_emp_id: "",
        faculty_user_id: "",
        created_by: " "
      },
      id: "",
      name: "",
      description: "",
      hashtags: [],
      material_tags:{},
      duration_minutes: 0,
      type: "ASSET_LIBRARY",
      sub_type: "IMAGE",
      review_details: {
        reviewed_by: "",
        reviewed_on: 0,
        comments: ""
      }
    },
    filename: "image_upload_test1.PNG",
    isPrivate: "true"
  };

const headers = {
    'Content-Type': 'application/json',
    Authorization: token
};


async function getMaterialIdFromBulkCreate(file_name,source_id) {
  
    const payload = {
      requests: [taxonomyPayloadTemplate]
    };

    payload["requests"][0]["filename"] = "testFileName";
    payload["requests"][0]["learning_material"]["name"] = file_name;

    payload["requests"][0]["learning_material"]["material_tags"] = {
        source_id: source_id
    };

    console.log(JSON.stringify(payload));

    
  
    try {
      const response = await fetch("https://bff.allen-stage.in/internal-bff/api/v1/learningMaterials/bulk_create", {
        method: "POST",
        headers: headers,
        body: JSON.stringify(payload)
      });
  
      const result = await response.json();
      const id = result["data"]["materials"][0]["id"];
      console.log(JSON.stringify(result, null, 2))
      return id;
    } catch (error) {
      console.error("Error during bulk create:", error);
      return null;
    }
  }

function downloadImage(imageUrl) {
    return new Promise((resolve, reject) => {
      const parsedUrl = new URL(imageUrl); // Use URL constructor for ES Modules
      const fileName = path.basename(parsedUrl.pathname);
      if (!fs.existsSync(image_asset_output_folder)) {
        fs.mkdirSync(image_asset_output_folder, { recursive: true });
      }

      const filePath = path.join(image_asset_output_folder, fileName);
      const file = fs.createWriteStream(filePath);
  
      https.get(imageUrl, (response) => {
        if (response.statusCode === 200) {
          response.pipe(file);
          file.on('finish', () => {
            file.close();
            console.log(`✅ Successfully downloaded: ${filePath}`);
            resolve(filePath);
          });
        } else {
          file.close();
          fs.unlink(filePath, () => {});
          console.error(`❌ Failed to download. HTTP Status: ${response.statusCode}`);
          reject(new Error(`Download failed. Status: ${response.statusCode}`));
        }
      }).on('error', (err) => {
        file.close();
        fs.unlink(filePath, () => {});
        console.error(`❌ Error downloading image: ${err.message}`);
        reject(err);
      });
    });
}
  

async function initMultipartUpload(id, fileFormat,isPublic) {
  console.log("in initMultipartUpload ");
  const url = `https://bff.allen-stage.in/internal-bff/api/v1/learningMaterials/${id}/init_multipart_upload`;

  const payload = JSON.stringify({
    file_format: fileFormat,
    public:isPublic
  })

  console.log(`in initMultipartUpload ${payload}`)

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: payload
    });

    console.log(JSON.stringify(response));

    if (response.status === 200) {
      const result = await response.json();
      return result.data.upload_data.upload_id; // ✅ This returns just the ID
    } else {
      console.error('❌ Error at multipart_upload:', response.status);
      return null;
    }
  } catch (err) {
    console.error('❌ Exception during multipart_upload:', err.message);
    return null;
  }
}


async function uploadPart(id, uploadId) {
  const url = `https://bff.allen-stage.in/internal-bff/api/v1/learningMaterials/${id}/upload_part`;

  const payload = JSON.stringify({
    part_number: 1,
    upload_id: uploadId
  });

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: payload
    });

    if (response.status === 200) {
      const result = await response.json();
      return result.data.upload_data.presigned_url;
    } else {
      console.error('❌ Error at uploadPart. Status:', response.status);
      return null;
    }
  } catch (err) {
    console.error('❌ Exception during uploadPart:', err.message);
    return null;
  }
}

async function uploadFile(upload_presigned_url, filename) {
    try {
      const payload = await fsPromise.readFile(filename);
  
      const response = await fetch(upload_presigned_url, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json' // You can set the actual file mime type if needed
        },
        body: payload
      });
  
      if (response.status == 200) {
        const etag = response.headers.get('ETag');
        return etag;
        
      } else {
        console.error('Error at upload_file:', response.status);
        return null;
      }
    } catch (error) {
      console.error('Exception during upload_file:', error.message);
      return null;
    }
}

  async function completeUpload(id, etag, uploadId) {
    const url = `https://bff.allen-stage.in/internal-bff/api/v1/learningMaterials/${id}/complete_multipart_upload`;
  
    const payload = JSON.stringify({
      upload_id: uploadId,
      parts: [
        {
          part_number: 1,
          etag: etag
        }
      ]
    });
  
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: payload
      });
  
      if (response.status === 200) {
        const result = await response.json();
        return result.data.id;
      } else {
        console.error('Error at complete upload:', response.status);
        return null;
      }
    } catch (error) {
      console.error('Exception at complete upload:', error.message);
      return null;
    }
  }

async function fetchMaterialInfo(id) {
    const url = 'https://bff.allen-stage.in/lmm/MaterialInfoWithFileContentBulk';
  
    const body = {
      ids: [id],
      include_raw_data: false,
      include_secondary_content: false
    };
  
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(body)
      });

      if(response.status == 200){
        const data = await response.json();
        if(data["data"][id]["error"]!="")
        {
            console.log("error occured");
            return null;
        }
        //console.log(JSON.stringify(data, null, 2));
        return data["data"][id]["original_file_content"]["presigned_url"];
      } else{

      }
  
    } catch {
      console.error('Failed to fetch material info:');
    }
}

async function getCDNUrl(id){
    const url = `https://bff.allen-stage.in/v1/cal-svc/presigned_urls`
    const body = {
        content_ids:[id]
    };

    try {
        const response = await fetch(url, {
          method: 'POST',
          headers: headers,
          body: JSON.stringify(body)
        });
  
        if(response.status == 200){
          const data = await response.json();
          if(data["data"][0]["error"]!="")
          {
            console.log("error occured");
            return null;
          }

          return data["data"][0]["presignedUrl"];
        } else{
  
        }
    
      } catch {
        console.error('Failed to fetch material info:');
      }

}


export async function UploadImage(imageUrl,source_id) {
    try{
        const parsedUrl = new URL(imageUrl); // Example: 'https://example.com/images/photo.png'
        const fileNameWithExt = path.basename(parsedUrl.pathname); // 'photo.png'

        const file_name = path.parse(fileNameWithExt).name;

        console.log(file_name);

        const c_id = await getMaterialIdFromBulkCreate(file_name,source_id);
        console.log(c_id);

        const filePath = await downloadImage(imageUrl);


        const upload_id = await initMultipartUpload(c_id,"jpg",true);
        const upload_url = await uploadPart(c_id,upload_id);
        const e_tag = await uploadFile(upload_url,filePath);
        const id = await completeUpload(c_id,e_tag,upload_id);

        console.log(`Execution Success final id is ${id}`);

        const download_url = await getCDNUrl(c_id);
        console.log(download_url);
        return download_url;
    } catch{
        console.error('error in upload :')
        return null;
    }
    
}

//UploadImage("https://cdn.mathpix.com/cropped/2025_05_02_63c4d213a5307d5e68c4g-01.jpg?height=678&width=1103&top_left_y=575&top_left_x=174");