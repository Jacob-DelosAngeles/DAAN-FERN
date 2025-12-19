import requests
import os
import sys

# Add parent directory to path to import models if needed, but we are testing via API
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"
FILENAME = "sample_sensor_data.csv"
FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), FILENAME)

def test_iri_computation():
    print(f"Testing IRI computation with {FILENAME}...")
    
    # 1. Upload File
    url = f"{BASE_URL}/upload/"
    if not os.path.exists(FILE_PATH):
        print(f"Error: File {FILE_PATH} not found.")
        return

    with open(FILE_PATH, 'rb') as f:
        files = {'file': (FILENAME, f, 'text/csv')}
        response = requests.post(url, files=files)
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return
    
    upload_data = response.json()
    uploaded_filename = upload_data['filename']
    print(f"Upload successful. Filename: {uploaded_filename}")

    # 2. Compute IRI
    compute_url = f"{BASE_URL}/iri/compute/{uploaded_filename}?segment_length=100"
    response = requests.post(compute_url, json={})
    
    if response.status_code != 200:
        print(f"Computation failed: {response.text}")
        return
    
    result = response.json()
    print("Computation successful!")
    
    # 3. Verify Response Structure
    print(f"Total Segments: {result.get('total_segments')}")
    
    # Check Chart Data
    raw_data = result.get('raw_data')
    filtered_data = result.get('filtered_data')
    
    if raw_data and len(raw_data) > 0:
        print(f"✅ Raw Data present: {len(raw_data)} points")
        print(f"   Sample: {raw_data[0]}")
    else:
        print("❌ Raw Data MISSING or empty")
        
    if filtered_data and len(filtered_data) > 0:
        print(f"✅ Filtered Data present: {len(filtered_data)} points")
        print(f"   Sample: {filtered_data[0]}")
    else:
        print("❌ Filtered Data MISSING or empty")

    # Check Segments Coordinates
    segments = result.get('segments', [])
    if segments:
        first_seg = segments[0]
        print(f"✅ Segments present. Checking first segment...")
        print(f"   Start Lat: {first_seg.get('start_lat')}")
        print(f"   Start Lon: {first_seg.get('start_lon')}")
        
        if first_seg.get('start_lat') is not None:
            print("✅ Coordinates present in segment")
        else:
            print("❌ Coordinates MISSING in segment")
    else:
        print("❌ No segments returned")

if __name__ == "__main__":
    test_iri_computation()
