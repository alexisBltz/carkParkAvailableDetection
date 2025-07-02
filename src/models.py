"""
Modelos de datos para el sistema de estacionamiento
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import json

@dataclass
class ParkingSpace:
    """Representa un espacio de estacionamiento"""
    x: int
    y: int
    width: int
    height: int
    id: Optional[str] = None
    confidence: float = 0.0
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def area(self) -> int:
        return self.width * self.height
    
    def contains_point(self, x: int, y: int) -> bool:
        """Verifica si un punto está dentro del espacio"""
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convierte a tupla (x, y, w, h)"""
        return (self.x, self.y, self.width, self.height)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'id': self.id,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingSpace':
        """Crea instancia desde diccionario"""
        return cls(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            id=data.get('id'),
            confidence=data.get('confidence', 0.0)
        )
    
    def copy(self) -> 'ParkingSpace':
        """Crea una copia del espacio"""
        return ParkingSpace(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            id=self.id,
            confidence=self.confidence
        )

@dataclass
class OccupancyStatus:
    """Estado de ocupación de un espacio"""
    space_id: str
    is_occupied: bool
    confidence: float
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'space_id': self.space_id,
            'is_occupied': self.is_occupied,
            'confidence': self.confidence,
            'timestamp': self.timestamp
        }

@dataclass
class AnalysisStats:
    """Estadísticas del análisis"""
    total_spaces: int
    occupied_spaces: int
    free_spaces: int
    occupancy_rate: float
    timestamp: str
    
    @property
    def availability_rate(self) -> float:
        return 100.0 - self.occupancy_rate
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_spaces': self.total_spaces,
            'occupied_spaces': self.occupied_spaces,
            'free_spaces': self.free_spaces,
            'occupancy_rate': self.occupancy_rate,
            'availability_rate': self.availability_rate,
            'timestamp': self.timestamp
        }
