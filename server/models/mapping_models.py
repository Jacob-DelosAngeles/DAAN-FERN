from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class MapPoint(BaseModel):
    lat: float
    lon: float

class VehicleMarker(BaseModel):
    lat: float
    lon: float
    vehicle_type: str
    count: int
    popup_html: str
    tooltip: str
    color: str
    icon: str

class PotholeMarker(BaseModel):
    lat: float
    lon: float
    confidence: float
    image_path: str
    image_url: str
    popup_html: str
    tooltip: str

class PavementSegment(BaseModel):
    points: List[List[float]]  # [[lat, lon], [lat, lon], ...]
    type: str
    color: str

class MappingResponse(BaseModel):
    success: bool
    message: str
    data: Any
    total_items: int

class VehicleMappingResponse(MappingResponse):
    data: List[VehicleMarker]

class PotholeMappingResponse(MappingResponse):
    data: List[PotholeMarker]

class PavementMappingResponse(MappingResponse):
    data: List[PavementSegment]
