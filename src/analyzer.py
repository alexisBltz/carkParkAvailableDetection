"""
Análisis de ocupación de espacios de estacionamiento
"""
import cv2
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from .models import ParkingSpace, OccupancyStatus, AnalysisStats

class OccupancyAnalyzer:
    """Analiza la ocupación de espacios de estacionamiento"""
    
    def __init__(self):
        self.threshold_fixed = 0.3
        self.threshold_adaptive = 0.4
        self.background_models = {}
        self.history_length = 5
        self.occupancy_history = {}
        
    def analyze_fixed_threshold(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> List[OccupancyStatus]:
        """Análisis con umbral fijo"""
        results = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for space in spaces:
            # Extraer ROI
            roi = gray[space.y:space.y + space.height, space.x:space.x + space.width]
            if roi.size == 0:
                continue
            
            # Calcular densidad de píxeles
            mean_intensity = np.mean(roi)
            normalized_intensity = mean_intensity / 255.0
            
            # Determinar ocupación
            is_occupied = normalized_intensity < self.threshold_fixed
            confidence = abs(normalized_intensity - 0.5) * 2  # 0.5 es el punto medio
            
            status = OccupancyStatus(
                space_id=space.id or f"space_{id(space)}",
                is_occupied=is_occupied,
                confidence=confidence,
                timestamp=datetime.now().isoformat()
            )
            results.append(status)
        
        return results
    
    def analyze_adaptive_threshold(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> List[OccupancyStatus]:
        """Análisis con umbral adaptativo"""
        results = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for space in spaces:
            roi = gray[space.y:space.y + space.height, space.x:space.x + space.width]
            if roi.size == 0:
                continue
            
            # Umbral adaptativo local
            adaptive_thresh = cv2.adaptiveThreshold(
                roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Calcular porcentaje de píxeles oscuros
            dark_pixels = np.sum(adaptive_thresh == 0)
            total_pixels = roi.size
            dark_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0
            
            # Determinar ocupación
            is_occupied = dark_ratio > self.threshold_adaptive
            confidence = abs(dark_ratio - 0.5) * 2
            
            status = OccupancyStatus(
                space_id=space.id or f"space_{id(space)}",
                is_occupied=is_occupied,
                confidence=confidence,
                timestamp=datetime.now().isoformat()
            )
            results.append(status)
        
        return results
    
    def analyze_background_subtraction(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> List[OccupancyStatus]:
        """Análisis usando sustracción de fondo"""
        results = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for space in spaces:
            space_id = space.id or f"space_{id(space)}"
            
            # Inicializar modelo de fondo si no existe
            if space_id not in self.background_models:
                self.background_models[space_id] = cv2.createBackgroundSubtractorMOG2(
                    detectShadows=True, varThreshold=50
                )
            
            roi = gray[space.y:space.y + space.height, space.x:space.x + space.width]
            if roi.size == 0:
                continue
            
            # Aplicar sustractor de fondo
            bg_model = self.background_models[space_id]
            fg_mask = bg_model.apply(roi)
            
            # Calcular área de primer plano
            fg_area = np.sum(fg_mask == 255)
            total_area = roi.size
            fg_ratio = fg_area / total_area if total_area > 0 else 0
            
            # Determinar ocupación
            is_occupied = fg_ratio > 0.15  # Umbral de movimiento/cambio
            confidence = min(fg_ratio * 3, 1.0)  # Escalar confianza
            
            status = OccupancyStatus(
                space_id=space_id,
                is_occupied=is_occupied,
                confidence=confidence,
                timestamp=datetime.now().isoformat()
            )
            results.append(status)
        
        return results
    
    def analyze_with_history(self, frame: np.ndarray, spaces: List[ParkingSpace], 
                           method: str = "adaptive") -> List[OccupancyStatus]:
        """Análisis con historial para estabilizar resultados"""
        
        # Obtener análisis actual
        if method == "fixed":
            current_results = self.analyze_fixed_threshold(frame, spaces)
        elif method == "background":
            current_results = self.analyze_background_subtraction(frame, spaces)
        else:  # adaptive
            current_results = self.analyze_adaptive_threshold(frame, spaces)
        
        # Procesar con historial
        stabilized_results = []
        
        for status in current_results:
            space_id = status.space_id
            
            # Inicializar historial si no existe
            if space_id not in self.occupancy_history:
                self.occupancy_history[space_id] = []
            
            # Agregar resultado actual
            self.occupancy_history[space_id].append(status.is_occupied)
            
            # Mantener solo los últimos N resultados
            if len(self.occupancy_history[space_id]) > self.history_length:
                self.occupancy_history[space_id].pop(0)
            
            # Decidir basado en mayoría en el historial
            history = self.occupancy_history[space_id]
            occupied_count = sum(history)
            is_occupied_stable = occupied_count > len(history) / 2
            
            # Calcular confianza basada en consistencia
            consistency = max(occupied_count, len(history) - occupied_count) / len(history)
            final_confidence = status.confidence * consistency
            
            stabilized_status = OccupancyStatus(
                space_id=space_id,
                is_occupied=is_occupied_stable,
                confidence=final_confidence,
                timestamp=status.timestamp
            )
            stabilized_results.append(stabilized_status)
        
        return stabilized_results
    
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
    
    def reset_background_models(self):
        """Reinicia los modelos de fondo"""
        self.background_models.clear()
    
    def reset_history(self):
        """Reinicia el historial de ocupación"""
        self.occupancy_history.clear()
    
    def get_space_trend(self, space_id: str) -> Optional[str]:
        """Obtiene la tendencia de un espacio específico"""
        if space_id not in self.occupancy_history:
            return None
        
        history = self.occupancy_history[space_id]
        if len(history) < 3:
            return "insufficient_data"
        
        recent = history[-3:]
        if all(recent):
            return "consistently_occupied"
        elif not any(recent):
            return "consistently_free"
        elif recent[-1] and not recent[0]:
            return "recently_occupied"
        elif not recent[-1] and recent[0]:
            return "recently_freed"
        else:
            return "fluctuating"
