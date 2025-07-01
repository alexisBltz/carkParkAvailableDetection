"""
Analizador basado en el código exitoso de main.py
Replica exactamente el preprocesamiento y detección que funciona
"""
import cv2
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from .models import ParkingSpace, OccupancyStatus, AnalysisStats

class WorkingOccupancyAnalyzer:
    """Analizador basado en el código que REALMENTE funciona"""
    
    def __init__(self, pixel_threshold: int = 900):
        """
        Args:
            pixel_threshold: Umbral de píxeles blancos para determinar ocupación
                           < pixel_threshold = LIBRE (espacio vacío)
                           >= pixel_threshold = OCUPADO (hay un auto)
        """
        self.pixel_threshold = pixel_threshold
        
    def analyze_spaces(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> List[OccupancyStatus]:
        """
        Analiza espacios usando el método que REALMENTE funciona
        Replica exactamente el main.py exitoso
        """
        results = []
        
        # PREPROCESAMIENTO EXACTO del main.py que funciona
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(
            img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 25, 16
        )
        img_median = cv2.medianBlur(img_threshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_processed = cv2.dilate(img_median, kernel, iterations=1)
        
        for space in spaces:
            try:
                # Extraer exactamente como en main.py
                x, y = space.x, space.y
                width, height = space.width, space.height
                
                # Recortar región del espacio
                img_crop = img_processed[y:y + height, x:x + width]
                
                if img_crop.size == 0:
                    continue
                
                # DETECCIÓN EXACTA: contar píxeles blancos
                pixel_count = cv2.countNonZero(img_crop)
                
                # LÓGICA EXACTA del main.py:
                # count < 900 = LIBRE (color verde)
                # count >= 900 = OCUPADO (color rojo)
                is_occupied = pixel_count >= self.pixel_threshold
                
                # Calcular confianza basada en qué tan lejos está del umbral
                distance_from_threshold = abs(pixel_count - self.pixel_threshold)
                max_pixels = width * height  # Máximo posible
                confidence = min(distance_from_threshold / (max_pixels * 0.3), 1.0)
                
                space_id = space.id or f"space_{len(results)}"
                status = OccupancyStatus(
                    space_id=space_id,
                    is_occupied=is_occupied,
                    confidence=confidence,
                    timestamp=datetime.now().isoformat()
                )
                results.append(status)
                
            except Exception as e:
                # Error fallback
                space_id = space.id or f"space_{len(results)}"
                status = OccupancyStatus(
                    space_id=space_id,
                    is_occupied=False,
                    confidence=0.0,
                    timestamp=datetime.now().isoformat()
                )
                results.append(status)
        
        return results
    
    def analyze_with_debug_info(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> List[Dict]:
        """
        Análisis con información detallada para debugging
        Devuelve la misma info que muestra el main.py original
        """
        results = []
        
        # Mismo preprocesamiento
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(
            img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 25, 16
        )
        img_median = cv2.medianBlur(img_threshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_processed = cv2.dilate(img_median, kernel, iterations=1)
        
        for i, space in enumerate(spaces):
            try:
                x, y = space.x, space.y
                width, height = space.width, space.height
                
                img_crop = img_processed[y:y + height, x:x + width]
                
                if img_crop.size == 0:
                    continue
                
                pixel_count = cv2.countNonZero(img_crop)
                is_occupied = pixel_count >= self.pixel_threshold
                
                # Info detallada como en main.py
                debug_info = {
                    'space_index': i,
                    'space_id': space.id or f"space_{i}",
                    'position': (x, y),
                    'size': (width, height),
                    'pixel_count': pixel_count,
                    'threshold': self.pixel_threshold,
                    'is_occupied': is_occupied,
                    'status': 'OCUPADO' if is_occupied else 'LIBRE',
                    'color': (0, 0, 255) if is_occupied else (0, 255, 0),  # Rojo/Verde
                    'thickness': 2 if is_occupied else 5  # Como en main.py
                }
                results.append(debug_info)
                
            except Exception as e:
                debug_info = {
                    'space_index': i,
                    'space_id': space.id or f"space_{i}",
                    'error': str(e),
                    'pixel_count': 0,
                    'is_occupied': False
                }
                results.append(debug_info)
        
        return results
    
    def get_processed_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Devuelve el frame procesado exactamente como en main.py
        Útil para debugging visual
        """
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(
            img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 25, 16
        )
        img_median = cv2.medianBlur(img_threshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_processed = cv2.dilate(img_median, kernel, iterations=1)
        
        return img_processed
    
    def visualize_analysis(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> np.ndarray:
        """
        Visualiza el análisis exactamente como main.py
        Devuelve frame con rectángulos y contadores
        """
        # Obtener análisis detallado
        debug_results = self.analyze_with_debug_info(frame, spaces)
        
        # Trabajar sobre copia del frame original
        img_result = frame.copy()
        
        space_counter = 0  # Contador de espacios libres
        
        for debug_info in debug_results:
            if 'error' in debug_info:
                continue
                
            x, y = debug_info['position']
            width, height = debug_info['size']
            pixel_count = debug_info['pixel_count']
            color = debug_info['color']
            thickness = debug_info['thickness']
            
            if not debug_info['is_occupied']:
                space_counter += 1
            
            # Dibujar rectángulo como en main.py
            cv2.rectangle(img_result, (x, y), (x + width, y + height), color, thickness)
            
            # Mostrar conteo de píxeles como en main.py
            try:
                # Simular cvzone.putTextRect con cv2.putText
                text = str(pixel_count)
                cv2.putText(img_result, text, (x, y + height - 3), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            except:
                pass
        
        # Mostrar total como en main.py
        total_spaces = len([r for r in debug_results if 'error' not in r])
        status_text = f'Free: {space_counter}/{total_spaces}'
        cv2.putText(img_result, status_text, (100, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 0), 2)
        
        return img_result
    
    def calculate_statistics(self, occupancy_results: List[OccupancyStatus]) -> AnalysisStats:
        """Calcula estadísticas generales"""
        total_spaces = len(occupancy_results)
        occupied_spaces = sum(1 for result in occupancy_results if result.is_occupied)
        free_spaces = total_spaces - occupied_spaces
        
        occupancy_rate = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
        
        return AnalysisStats(
            total_spaces=total_spaces,
            occupied_spaces=occupied_spaces,
            free_spaces=free_spaces,
            occupancy_rate=occupancy_rate,
            timestamp=datetime.now().isoformat()
        )
    
    def set_pixel_threshold(self, threshold: int):
        """Actualiza el umbral de píxeles"""
        self.pixel_threshold = max(0, threshold)
    
    def get_pixel_threshold(self) -> int:
        """Obtiene el umbral actual de píxeles"""
        return self.pixel_threshold
