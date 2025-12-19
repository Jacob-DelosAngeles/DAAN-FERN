# Project DAAN Express Backend API

A FastAPI backend service for processing sensor data and computing International Roughness Index (IRI) values for road quality assessment.

## Features

- **File Upload**: Upload CSV files containing sensor data
- **IRI Computation**: Process sensor data to compute IRI values using your existing calculator
- **Data Validation**: Validate file format and data quality
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Configured for React frontend integration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### File Upload
- `POST /api/upload/` - Upload a CSV file
- `GET /api/upload/files` - List uploaded files
- `GET /api/upload/preview/{filename}` - Preview file contents
- `DELETE /api/upload/{filename}` - Delete a file

### IRI Computation
- `POST /api/iri/compute/{filename}` - Compute IRI with full parameters
- `GET /api/iri/compute/{filename}` - Compute IRI with query parameters
- `GET /api/iri/validate/{filename}` - Validate file for IRI computation
- `GET /api/iri/status` - Get service status

### General
- `GET /` - API root
- `GET /health` - Health check

## File Format Requirements

The uploaded CSV files must contain the following columns:
- `time` - Timestamp (ISO format or Unix timestamp)
- `ax` - X-axis acceleration (m/s²)
- `ay` - Y-axis acceleration (m/s²)
- `az` - Z-axis acceleration (m/s²)

Optional columns:
- `latitude` - GPS latitude
- `longitude` - GPS longitude
- `speed` - Vehicle speed (m/s)
- `altitude` - GPS altitude
- `wx`, `wy`, `wz` - Gyroscope data (rad/s)

## Usage Example

1. Upload a file:
```bash
curl -X POST "http://localhost:8000/api/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_sensor_data.csv"
```

2. Compute IRI:
```bash
curl -X GET "http://localhost:8000/api/iri/compute/your_file.csv?segment_length=100&cutoff_freq=10.0"
```

## Integration with React Frontend

This backend is designed to work with the React frontend in the `migration` folder. The CORS settings are configured to allow requests from:
- `http://localhost:3000` (Create React App)
- `http://localhost:5173` (Vite)

## Project Structure

```
migration_backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Dependencies
├── models/                 # Pydantic models
│   └── iri_models.py
├── services/               # Business logic
│   └── iri_service.py
├── api/                    # API routes
│   └── routes/
│       ├── upload.py
│       └── iri.py
├── utils/                  # Utility functions
│   └── file_handler.py
└── uploads/                # Uploaded files (created automatically)
```

## Development

The backend integrates with your existing IRI calculator in `../utils/iri_calculator.py` without modification, ensuring compatibility with your current Streamlit application.
