"""
Detección inteligente de espacios de estacionamiento
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
from .models import ParkingSpace

class SmartDetector:
    """Detector inteligente de espacios de estacionamiento"""
    
    def __init__(self):
        self.min_area = 1000
        self.max_area = 50000
        self.aspect_ratio_range = (0.5, 3.0)
        self.merge_distance = 50
        
    def detect_spaces_contours(self, image: np.ndarray) -> List[ParkingSpace]:
        """Detecta espacios usando contornos"""
        try:
            # Preprocesamiento
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detección de bordes adaptativa
            edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY, 11, 2)
            
            # Morfología para limpiar
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            spaces = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if self.min_area <= area <= self.max_area:
                    # Aproximar contorno a rectángulo
                    rect = cv2.boundingRect(contour)
                    x, y, w, h = rect
                    
                    # Verificar aspect ratio
                    aspect_ratio = w / h if h > 0 else 0
                    if self.aspect_ratio_range[0] <= aspect_ratio <= self.aspect_ratio_range[1]:
                        confidence = min(area / self.max_area, 1.0)
                        space = ParkingSpace(x, y, w, h, confidence=confidence)
                        spaces.append(space)
            
            # Fusionar espacios cercanos
            return self._merge_overlapping_spaces(spaces)
            
        except Exception as e:
            print(f"Error en detección por contornos: {e}")
            return []
    
    def detect_spaces_lines(self, image: np.ndarray) -> List[ParkingSpace]:
        """Detecta espacios usando líneas de Hough"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blur, 50, 150, apertureSize=3)
            
            # Detectar líneas
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                  minLineLength=30, maxLineGap=10)
            
            if lines is None:
                return []
            
            # Agrupar líneas en rectángulos potenciales
            horizontal_lines = []
            vertical_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                
                if abs(angle) < 30 or abs(angle) > 150:  # Líneas horizontales
                    horizontal_lines.append(line[0])
                elif 60 < abs(angle) < 120:  # Líneas verticales
                    vertical_lines.append(line[0])
            
            # Formar rectángulos
            spaces = self._form_rectangles_from_lines(horizontal_lines, vertical_lines)
            return spaces
            
        except Exception as e:
            print(f"Error en detección por líneas: {e}")
            return []
    
    def detect_spaces_template(self, image: np.ndarray, template_size: Tuple[int, int] = (80, 40)) -> List[ParkingSpace]:
        """Detecta espacios usando template matching"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Crear template básico (rectángulo)
            template = np.zeros(template_size[::-1], dtype=np.uint8)
            cv2.rectangle(template, (2, 2), (template_size[0]-2, template_size[1]-2), 255, 2)
            
            # Template matching
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.3)
            
            spaces = []
            for pt in zip(*locations[::-1]):
                x, y = pt
                w, h = template_size
                confidence = float(result[y, x])
                space = ParkingSpace(x, y, w, h, confidence=confidence)
                spaces.append(space)
            
            return self._merge_overlapping_spaces(spaces)
            
        except Exception as e:
            print(f"Error en template matching: {e}")
            return []
    
    def detect_spaces_combined(self, image: np.ndarray) -> List[ParkingSpace]:
        """Combina múltiples métodos de detección"""
        all_spaces = []
        
        # Método 1: Contornos
        contour_spaces = self.detect_spaces_contours(image)
        all_spaces.extend(contour_spaces)
        
        # Método 2: Líneas de Hough
        line_spaces = self.detect_spaces_lines(image)
        all_spaces.extend(line_spaces)
        
        # Método 3: Template matching
        template_spaces = self.detect_spaces_template(image)
        all_spaces.extend(template_spaces)
        
        # Fusionar y filtrar
        merged_spaces = self._merge_overlapping_spaces(all_spaces)
        
        # Asignar IDs
        for i, space in enumerate(merged_spaces):
            space.id = f"AUTO_{i:03d}"
        
        return merged_spaces
    
    def _merge_overlapping_spaces(self, spaces: List[ParkingSpace]) -> List[ParkingSpace]:
        """Fusiona espacios superpuestos"""
        if not spaces:
            return []
        
        merged = []
        spaces_sorted = sorted(spaces, key=lambda s: s.confidence, reverse=True)
        
        for space in spaces_sorted:
            should_merge = False
            for i, existing in enumerate(merged):
                if self._spaces_overlap(space, existing):
                    # Fusionar con el mejor
                    if space.confidence > existing.confidence:
                        merged[i] = space
                    should_merge = True
                    break
            
            if not should_merge:
                merged.append(space)
        
        return merged
    
    def _spaces_overlap(self, space1: ParkingSpace, space2: ParkingSpace) -> bool:
        """Verifica si dos espacios se superponen"""
        x1, y1, w1, h1 = space1.to_tuple()
        x2, y2, w2, h2 = space2.to_tuple()
        
        # Calcular superposición
        overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap_area = overlap_x * overlap_y
        
        area1 = w1 * h1
        area2 = w2 * h2
        min_area = min(area1, area2)
        
        return overlap_area > 0.3 * min_area
    
    def _form_rectangles_from_lines(self, h_lines: List, v_lines: List) -> List[ParkingSpace]:
        """Forma rectángulos a partir de líneas horizontales y verticales"""
        spaces = []
        
        for h_line in h_lines[:10]:  # Limitar para rendimiento
            for v_line in v_lines[:10]:
                # Encontrar intersección
                x1, y1, x2, y2 = h_line
                x3, y3, x4, y4 = v_line
                
                # Verificar si las líneas son perpendiculares aproximadamente
                if self._lines_intersect(h_line, v_line):
                    # Crear espacio tentativo
                    x = min(x1, x2, x3, x4)
                    y = min(y1, y2, y3, y4)
                    w = abs(max(x1, x2) - min(x1, x2))
                    h = abs(max(y3, y4) - min(y3, y4))
                    
                    if w > 30 and h > 20 and w < 200 and h < 100:
                        space = ParkingSpace(x, y, w, h, confidence=0.6)
                        spaces.append(space)
        
        return spaces
    
    def _lines_intersect(self, line1: List[int], line2: List[int]) -> bool:
        """Verifica si dos líneas se intersectan"""
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2
        
        # Calcular determinantes
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return False
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        return 0 <= t <= 1 and 0 <= u <= 1
