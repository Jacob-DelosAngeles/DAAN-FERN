import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import os
from models.mapping_models import VehicleMarker, PotholeMarker, PavementSegment

class MappingService:
    
    def process_vehicle_data(self, file_paths: List[str]) -> Tuple[List[VehicleMarker], int]:
        """
        Process vehicle detection CSV files and return map markers
        """
        merged_df = self._merge_csvs(file_paths, ['latitude', 'longitude', 'vehicle_type'])
        if merged_df is None or len(merged_df) == 0:
            return [], 0
            
        # Filter valid types
        valid_types = ['car', 'bicycle', 'truck', 'motorcycle']
        # Normalize bicycle to motorcycle as in original app
        merged_df['vehicle_type'] = merged_df['vehicle_type'].replace('bicycle', 'motorcycle')
        df_filtered = merged_df[merged_df['vehicle_type'].isin(valid_types)].copy()
        
        markers = []
        vehicle_counts = df_filtered['vehicle_type'].value_counts()
        
        vehicle_config = {
            'car': {'color': 'blue', 'icon': 'car', 'tooltip': '🚗 Car'},
            'truck': {'color': 'orange', 'icon': 'truck', 'tooltip': '🚛 Truck'},
            'motorcycle': {'color': 'green', 'icon': 'motorcycle', 'tooltip': '🏍️ Motorcycle'}
        }
        
        for idx, row in df_filtered.iterrows():
            try:
                v_type = row['vehicle_type']
                config = vehicle_config.get(v_type, {'color': 'gray', 'icon': 'question', 'tooltip': '❓ Unknown'})
                
                markers.append(VehicleMarker(
                    lat=float(row['latitude']),
                    lon=float(row['longitude']),
                    vehicle_type=v_type,
                    count=int(vehicle_counts.get(v_type, 0)),
                    popup_html=f"Type: {v_type.title()}<br>Count: {vehicle_counts.get(v_type, 0)}",
                    tooltip=config['tooltip'],
                    color=config['color'],
                    icon=config['icon']
                ))
            except Exception:
                continue
                
        return markers, len(markers)

    def process_pothole_data(self, file_paths: List[str]) -> Tuple[List[PotholeMarker], int]:
        """
        Process pothole detection CSV files and return map markers
        """
        merged_df = self._merge_csvs(file_paths, ['latitude', 'longitude', 'image_path', 'confidence_score'])
        if merged_df is None or len(merged_df) == 0:
            return [], 0
            
        markers = []
        base_url = "https://pub-3acbf94b790d4e7cb2e8bed9bf68f024.r2.dev"
        
        for idx, row in merged_df.iterrows():
            try:
                image_path = row['image_path']
                image_url = f"{base_url}/{image_path}"
                confidence = float(row['confidence_score'])
                
                markers.append(PotholeMarker(
                    lat=float(row['latitude']),
                    lon=float(row['longitude']),
                    confidence=confidence,
                    image_path=image_path,
                    image_url=image_url,
                    popup_html=f"Pothole<br>Confidence: {confidence:.2%}",
                    tooltip=f"Pothole ({confidence:.1%})"
                ))
            except Exception:
                continue
                
        return markers, len(markers)

    def process_pavement_data(self, file_paths: List[str]) -> Tuple[List[PavementSegment], int]:
        """
        Process pavement type CSV files and return map segments
        """
        merged_df = self._merge_csvs(file_paths, ['latitude', 'longitude', 'type'])
        if merged_df is None or len(merged_df) == 0:
            return [], 0
            
        segments = []
        color_map = {
            'soil': '#8B4513',      # Brown
            'gravel': '#FFFFFF',    # White
            'flexible': '#2F2F2F',  # Dark gray
            'rigid': '#D3D3D3'      # Whitish gray
        }
        
        if len(merged_df) < 2:
            return [], 0
            
        current_type = None
        current_points = []
        
        for idx, row in merged_df.iterrows():
            p_type = row['type']
            point = [float(row['latitude']), float(row['longitude'])]
            
            if current_type is not None and p_type != current_type:
                if len(current_points) >= 2:
                    segments.append(PavementSegment(
                        points=current_points.copy(),
                        type=current_type,
                        color=color_map.get(current_type, '#808080')
                    ))
                current_points = []
            
            current_points.append(point)
            current_type = p_type
            
        if len(current_points) >= 2:
            segments.append(PavementSegment(
                points=current_points,
                type=current_type,
                color=color_map.get(current_type, '#808080')
            ))
            
        return segments, len(segments)

    def _merge_csvs(self, file_paths: List[str], required_cols: List[str]) -> pd.DataFrame:
        dfs = []
        for path in file_paths:
            try:
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    # Check cols
                    if all(col in df.columns for col in required_cols):
                        # Validate numeric coords
                        if 'latitude' in df.columns:
                            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                        if 'longitude' in df.columns:
                            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                        df = df.dropna(subset=['latitude', 'longitude'])
                        dfs.append(df)
            except Exception:
                continue
        
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return None
