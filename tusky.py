import requests
import os
import base64
import random
import string
import time

API_KEYS = [
   "",
    # Thêm các API key khác nếu cần
]
folder_path = r"C:\profile-gpm"
# Tạo vault
def create_vault(vault_name, api_key):
    url = "https://api.tusky.io/vaults"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    data = {"name": vault_name}
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()["id"]
    else:
        raise Exception(f"❌ Failed to create vault: {response.status_code} - {response.text}")

# Khởi tạo upload
def initiate_upload(vault_id, file_path, api_key):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    if file_size <= 0:
        raise ValueError(f"Invalid file size: {file_size} bytes")
    
    # Encode filename và filetype
    encoded_filename = base64.b64encode(file_name.encode("utf-8")).decode("utf-8")
    filetype = os.path.splitext(file_name)[-1].replace('.', '') or 'bin'
    encoded_filetype = base64.b64encode(filetype.encode("utf-8")).decode("utf-8")

    upload_metadata = f"filename {encoded_filename},filetype {encoded_filetype}"
    
    headers = {
        "Api-Key": api_key,
        "Tus-Resumable": "1.0.0",
        "Upload-Length": str(file_size),
        "Upload-Metadata": upload_metadata
    }

    url = f"https://api.tusky.io/uploads?vaultId={vault_id}"
  #  print(f"🧾 File name: {file_name}, size: {file_size}")
   # print(f"Initiating upload with metadata: {upload_metadata}")
    #print(f"Headers: {headers}")
   # print(f"Upload URL: {url}")
    
    response = requests.post(url, headers=headers)
    
    request_id = response.headers.get("Request-Id")
   # print(f"Request ID: {request_id}")
    
    if response.status_code == 201:
        upload_url = response.headers.get("Location")
        if not upload_url:
            raise Exception("No Location header in response")
      
        return upload_url
    else:
        raise Exception(f"❌ Failed to initiate upload: {response.status_code} - {response.text}")

# Upload file
def upload_file_data(upload_url, file_path, api_key):
    with open(file_path, "rb") as f:
        file_data = f.read()

    headers = {
        "Tus-Resumable": "1.0.0",
        "Upload-Offset": "0",
        "Content-Type": "application/offset+octet-stream",
        "Api-Key": api_key
    }

    response = requests.patch(upload_url, headers=headers, data=file_data)
    if response.status_code == 201:
        print("✅ File uploaded successfully.")
    else:
        raise Exception(f"❌ Failed to upload file data: {response.status_code} - {response.text}")

# Lấy tệp ngẫu nhiên trong thư mục
def get_random_file_from_folder(folder_path):
    all_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]
    if not all_files:
        raise Exception("❌ Không có tệp nào trong thư mục.")
    return random.choice(all_files)

# === PROCESS ===


while True:
    for api_key in API_KEYS:
        try:
            file_path = get_random_file_from_folder(folder_path)
            print(f"\n📄 File selected: {file_path}")

            vault_name = "Vault_" + ''.join(random.choices(string.digits, k=6))
            vault_id = create_vault(vault_name, api_key)
            print(f"🔐 Vault '{vault_name}' created with ID: {vault_id}")

            upload_url = initiate_upload(vault_id, file_path, api_key)
            print(f"🚀 Upload started at: {upload_url}")

            upload_file_data(upload_url, file_path, api_key)

        except Exception as e:
            print(f"❗ Error: {e}")

    # Tuỳ chọn: nghỉ 3 giây giữa mỗi vòng để tránh spam API quá nhanh
    time.sleep(3)
