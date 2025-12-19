import requests
import os

API_URL = "http://localhost:8000/api/v1"
FILE_PATH = "/home/jacob/repos/DAAN/streamlit_package/pothole_data/pothole_detections.csv"

def test_pothole_flow():
    # 1. Upload File
    print(f"Uploading {FILE_PATH}...")
    with open(FILE_PATH, 'rb') as f:
        files = {'file': ('pothole_detections.csv', f, 'text/csv')}
        params = {'type': 'pothole'}
        upload_res = requests.post(f"{API_URL}/upload/", files=files, params=params)
    
    if upload_res.status_code != 200:
        print(f"Upload failed: {upload_res.text}")
        return

    upload_data = upload_res.json()
    filename = upload_data['filename']
    print(f"Uploaded filename: {filename}")

    # 2. Process File
    print(f"Processing {filename}...")
    process_res = requests.get(f"{API_URL}/pothole/process/{filename}")
    
    if process_res.status_code != 200:
        print(f"Processing failed: {process_res.text}")
        return

    process_data = process_res.json()
    print("Process Response Keys:", process_data.keys())
    
    if 'data' in process_data:
        data = process_data['data']
        print(f"Number of markers: {len(data)}")
        if len(data) > 0:
            print("First marker sample:", data[0])
            # Check for NaN
            for i, item in enumerate(data):
                if item['lat'] is None or item['lon'] is None:
                    print(f"Found None coordinates at index {i}")
    else:
        print("No 'data' key in response")

if __name__ == "__main__":
    test_pothole_flow()
