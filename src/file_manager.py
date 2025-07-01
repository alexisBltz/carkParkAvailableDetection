"""
Utilidades para manejo de archivos y persistencia
"""
import json
import pickle
import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import ParkingSpace, OccupancyStatus, AnalysisStats

class FileManager:
    """Gestiona la carga y guardado de archivos"""
    
    @staticmethod
    def save_spaces_json(spaces: List[ParkingSpace], filepath: str) -> bool:
        """Guarda espacios en formato JSON"""
        try:
            data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'spaces': [space.to_dict() for space in spaces]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando JSON: {e}")
            return False
    
    @staticmethod
    def load_spaces_json(filepath: str) -> List[ParkingSpace]:
        """Carga espacios desde formato JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            spaces = []
            spaces_data = data.get('spaces', [])
            for space_dict in spaces_data:
                space = ParkingSpace.from_dict(space_dict)
                spaces.append(space)
            
            return spaces
        except Exception as e:
            print(f"Error cargando JSON: {e}")
            return []
    
    @staticmethod
    def save_spaces_pickle(spaces: List[ParkingSpace], filepath: str) -> bool:
        """Guarda espacios en formato pickle (legacy)"""
        try:
            # Convertir a formato legacy para compatibilidad
            legacy_data = []
            for space in spaces:
                legacy_data.append(space.to_tuple())
            
            with open(filepath, 'wb') as f:
                pickle.dump(legacy_data, f)
            return True
        except Exception as e:
            print(f"Error guardando pickle: {e}")
            return False
    
    @staticmethod
    def load_spaces_pickle(filepath: str) -> List[ParkingSpace]:
        """Carga espacios desde formato pickle (legacy)"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            spaces = []
            for i, space_data in enumerate(data):
                if isinstance(space_data, (list, tuple)) and len(space_data) >= 4:
                    x, y, w, h = space_data[:4]
                    space = ParkingSpace(
                        x=int(x), y=int(y), 
                        width=int(w), height=int(h),
                        id=f"LEGACY_{i:03d}"
                    )
                    spaces.append(space)
            
            return spaces
        except Exception as e:
            print(f"Error cargando pickle: {e}")
            return []
    
    @staticmethod
    def auto_load_spaces(filepath: str) -> List[ParkingSpace]:
        """Carga espacios detectando automáticamente el formato"""
        if not os.path.exists(filepath):
            return []
        
        # Intentar JSON primero
        if filepath.lower().endswith('.json'):
            return FileManager.load_spaces_json(filepath)
        
        # Luego pickle
        try:
            return FileManager.load_spaces_pickle(filepath)
        except:
            # Si falla pickle, intentar JSON
            return FileManager.load_spaces_json(filepath)
    
    @staticmethod
    def export_analysis_csv(stats_history: List[AnalysisStats], filepath: str) -> bool:
        """Exporta estadísticas a CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Encabezados
                writer.writerow([
                    'Timestamp', 'Total_Spaces', 'Occupied_Spaces', 
                    'Free_Spaces', 'Occupancy_Rate', 'Availability_Rate'
                ])
                
                # Datos
                for stats in stats_history:
                    writer.writerow([
                        stats.timestamp,
                        stats.total_spaces,
                        stats.occupied_spaces,
                        stats.free_spaces,
                        f"{stats.occupancy_rate:.2f}",
                        f"{stats.availability_rate:.2f}"
                    ])
            
            return True
        except Exception as e:
            print(f"Error exportando CSV: {e}")
            return False
    
    @staticmethod
    def export_occupancy_csv(occupancy_history: List[List[OccupancyStatus]], filepath: str) -> bool:
        """Exporta historial de ocupación detallado a CSV"""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Encabezados
                writer.writerow(['Timestamp', 'Space_ID', 'Is_Occupied', 'Confidence'])
                
                # Datos
                for frame_results in occupancy_history:
                    for status in frame_results:
                        writer.writerow([
                            status.timestamp,
                            status.space_id,
                            'Yes' if status.is_occupied else 'No',
                            f"{status.confidence:.3f}"
                        ])
            
            return True
        except Exception as e:
            print(f"Error exportando ocupación CSV: {e}")
            return False
    
    @staticmethod
    def get_supported_video_formats() -> List[str]:
        """Retorna formatos de video soportados"""
        return ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    
    @staticmethod
    def get_supported_image_formats() -> List[str]:
        """Retorna formatos de imagen soportados"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tga']
    
    @staticmethod
    def validate_file_format(filepath: str, supported_formats: List[str]) -> bool:
        """Valida si un archivo tiene un formato soportado"""
        if not os.path.exists(filepath):
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        return ext in [fmt.lower() for fmt in supported_formats]
    
    @staticmethod
    def create_backup(filepath: str) -> Optional[str]:
        """Crea una copia de respaldo de un archivo"""
        try:
            if not os.path.exists(filepath):
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{filepath}.backup_{timestamp}"
            
            import shutil
            shutil.copy2(filepath, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error creando backup: {e}")
            return None
