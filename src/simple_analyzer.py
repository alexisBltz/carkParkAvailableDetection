"""
Análisis simple y efectivo de ocupación de espacios de estacionamiento
Basado en el enfoque directo de threshold simple
"""
import cv2
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from .models import ParkingSpace, OccupancyStatus, AnalysisStats

class SimpleOccupancyAnalyzer:
    """Analizador simple y efectivo de ocupación"""
    
    def __init__(self, threshold: float = 0.23):
        """
        Args:
            threshold: Umbral de intensidad para determinar ocupación (0.0 - 1.0)
                      Valores más bajos = más sensible a detectar ocupación
        """
        self.threshold = threshold
        
    def analyze_spaces(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> List[OccupancyStatus]:
        """
        Analiza la ocupación de espacios usando threshold simple
        
        Args:
            frame: Frame del video/imagen
            spaces: Lista de espacios a analizar
            
        Returns:
            Lista de estados de ocupación
        """
        results = []
        
        # Convertir a escala de grises para el análisis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for space in spaces:
            try:
                # Extraer región de interés (ROI)
                roi = gray[space.y:space.y + space.height, space.x:space.x + space.width]
                
                # Verificar que la ROI sea válida
                if roi.size == 0:
                    continue
                    
                # Calcular intensidad promedio normalizada
                mean_intensity = np.mean(roi)
                normalized_intensity = mean_intensity / 255.0
                
                # Determinar ocupación: espacios ocupados tienden a ser más oscuros
                is_occupied = normalized_intensity < self.threshold
                
                # Calcular confianza basada en qué tan lejos está del umbral
                distance_from_threshold = abs(normalized_intensity - self.threshold)
                confidence = min(distance_from_threshold * 4, 1.0)  # Escalar a 0-1
                
                # Crear resultado
                space_id = space.id or f"space_{len(results)}"
                status = OccupancyStatus(
                    space_id=space_id,
                    is_occupied=is_occupied,
                    confidence=confidence,
                    timestamp=datetime.now().isoformat()
                )
                results.append(status)
                
            except Exception as e:
                # En caso de error, marcar como desconocido
                space_id = space.id or f"space_{len(results)}"
                status = OccupancyStatus(
                    space_id=space_id,
                    is_occupied=False,
                    confidence=0.0,
                    timestamp=datetime.now().isoformat()
                )
                results.append(status)
        
        return results
    
    def analyze_with_preprocessing(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> List[OccupancyStatus]:
        """
        Análisis con preprocesamiento mejorado para mejor detección
        """
        results = []
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro gaussiano para reducir ruido
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        for space in spaces:
            try:
                # Extraer ROI
                roi = blurred[space.y:space.y + space.height, space.x:space.x + space.width]
                
                if roi.size == 0:
                    continue
                
                # Aplicar mejora de contraste local
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(roi)
                
                # Calcular estadísticas
                mean_intensity = np.mean(enhanced)
                std_intensity = np.std(enhanced)
                normalized_intensity = mean_intensity / 255.0
                
                # Usar tanto media como desviación estándar para mejor detección
                # Espacios ocupados tienden a tener menos variación (más uniformes)
                variability_factor = std_intensity / 255.0
                
                # Ajustar umbral basado en variabilidad
                adjusted_threshold = self.threshold + (variability_factor * 0.1)
                
                # Determinar ocupación
                is_occupied = normalized_intensity < adjusted_threshold
                
                # Confianza mejorada
                intensity_confidence = abs(normalized_intensity - adjusted_threshold) * 3
                variability_confidence = min(float(variability_factor * 2), 1.0)
                final_confidence = min((intensity_confidence + variability_confidence) / 2, 1.0)
                
                space_id = space.id or f"space_{len(results)}"
                status = OccupancyStatus(
                    space_id=space_id,
                    is_occupied=is_occupied,
                    confidence=final_confidence,
                    timestamp=datetime.now().isoformat()
                )
                results.append(status)
                
            except Exception as e:
                space_id = space.id or f"space_{len(results)}"
                status = OccupancyStatus(
                    space_id=space_id,
                    is_occupied=False,
                    confidence=0.0,
                    timestamp=datetime.now().isoformat()
                )
                results.append(status)
        
        return results
    
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
    
    def set_threshold(self, threshold: float):
        """Actualiza el umbral de detección"""
        self.threshold = max(0.0, min(1.0, threshold))  # Mantener entre 0 y 1
    
    def get_threshold(self) -> float:
        """Obtiene el umbral actual"""
        return self.threshold
    
    def debug_space_analysis(self, frame: np.ndarray, space: ParkingSpace) -> Dict:
        """
        Análisis detallado de un espacio específico para debug
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[space.y:space.y + space.height, space.x:space.x + space.width]
        
        if roi.size == 0:
            return {"error": "Invalid ROI"}
        
        mean_intensity = np.mean(roi)
        std_intensity = np.std(roi)
        min_intensity = np.min(roi)
        max_intensity = np.max(roi)
        normalized_intensity = mean_intensity / 255.0
        
        is_occupied = normalized_intensity < self.threshold
        
        return {
            "mean_intensity": float(mean_intensity),
            "std_intensity": float(std_intensity),
            "min_intensity": float(min_intensity),
            "max_intensity": float(max_intensity),
            "normalized_intensity": float(normalized_intensity),
            "threshold": self.threshold,
            "is_occupied": is_occupied,
            "roi_shape": roi.shape
        }
