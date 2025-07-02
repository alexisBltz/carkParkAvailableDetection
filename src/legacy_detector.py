"""
Detector Legacy - Funcionalidades del sistema original mejoradas
Integra las funcionalidades del código original con mejoras y modularización
"""
import cv2
import pickle
import numpy as np
from typing import List, Tuple, Optional, Callable
import os
from .models import ParkingSpace, OccupancyStatus
from datetime import datetime

try:
    import cvzone
    CVZONE_AVAILABLE = True
except ImportError:
    CVZONE_AVAILABLE = False
    print("⚠️  cvzone no está disponible. Algunas funcionalidades visuales estarán limitadas.")

class LegacySpaceEditor:
    """Editor de espacios basado en el código original mejorado"""
    
    def __init__(self, image_path: str, positions_file: str = "CarParkPos"):
        self.image_path = image_path
        self.positions_file = positions_file
        self.width = 107  # Ancho por defecto del espacio
        self.height = 48  # Alto por defecto del espacio
        self.pos_list = []
        self.image = None
        self.is_editing = False
        self.callback: Optional[Callable] = None
        
        # Cargar posiciones existentes
        self.load_positions()
        
    def load_positions(self):
        """Carga las posiciones desde archivo"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'rb') as f:
                    self.pos_list = pickle.load(f)
                print(f"✅ Cargadas {len(self.pos_list)} posiciones desde {self.positions_file}")
            else:
                self.pos_list = []
                print(f"📁 Archivo {self.positions_file} no encontrado. Iniciando con lista vacía.")
        except Exception as e:
            print(f"❌ Error cargando posiciones: {e}")
            self.pos_list = []
    
    def save_positions(self):
        """Guarda las posiciones en archivo"""
        try:
            with open(self.positions_file, 'wb') as f:
                pickle.dump(self.pos_list, f)
            print(f"💾 Guardadas {len(self.pos_list)} posiciones en {self.positions_file}")
            
            # Notificar al callback si existe
            if self.callback:
                spaces = self.get_parking_spaces()
                self.callback(spaces)
        except Exception as e:
            print(f"❌ Error guardando posiciones: {e}")
    
    def mouse_click(self, event, x, y, flags, params):
        """Maneja los clics del mouse para editar espacios"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Clic izquierdo: agregar espacio
            self.pos_list.append((x, y))
            print(f"➕ Agregado espacio en ({x}, {y})")
            self.save_positions()
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Clic derecho: eliminar espacio
            for i, pos in enumerate(self.pos_list):
                x1, y1 = pos
                if x1 < x < x1 + self.width and y1 < y < y1 + self.height:
                    removed_pos = self.pos_list.pop(i)
                    print(f"➖ Eliminado espacio en {removed_pos}")
                    self.save_positions()
                    break
    
    def start_editing(self, callback: Optional[Callable] = None):
        """Inicia el editor visual de espacios"""
        self.callback = callback
        
        if not os.path.exists(self.image_path):
            print(f"❌ Imagen no encontrada: {self.image_path}")
            return
        
        self.is_editing = True
        print("🖼️  Iniciando editor de espacios:")
        print("   • Clic izquierdo: Agregar espacio")
        print("   • Clic derecho: Eliminar espacio")
        print("   • Tecla 'q': Salir")
        print("   • Tecla 's': Cambiar tamaño de espacios")
        
        while self.is_editing:
            self.image = cv2.imread(self.image_path)
            
            if self.image is None:
                print(f"❌ No se pudo cargar la imagen: {self.image_path}")
                break
            
            # Dibujar espacios existentes
            for pos in self.pos_list:
                cv2.rectangle(self.image, pos, 
                            (pos[0] + self.width, pos[1] + self.height), 
                            (255, 0, 255), 2)
                
                # Mostrar número del espacio
                space_num = self.pos_list.index(pos) + 1
                cv2.putText(self.image, str(space_num), 
                          (pos[0] + 5, pos[1] + 20),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Mostrar información
            info_text = f"Espacios: {len(self.pos_list)} | Tamaño: {self.width}x{self.height}"
            cv2.putText(self.image, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Editor de Espacios", self.image)
            cv2.setMouseCallback("Editor de Espacios", self.mouse_click)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.is_editing = False
            elif key == ord('s'):
                self._change_space_size()
        
        cv2.destroyAllWindows()
        print("✅ Editor cerrado")
    
    def _change_space_size(self):
        """Permite cambiar el tamaño de los espacios"""
        print(f"Tamaño actual: {self.width}x{self.height}")
        try:
            new_width = int(input("Nuevo ancho (Enter para mantener actual): ") or self.width)
            new_height = int(input("Nueva altura (Enter para mantener actual): ") or self.height)
            self.width = max(20, new_width)  # Mínimo 20 píxeles
            self.height = max(20, new_height)
            print(f"✅ Nuevo tamaño: {self.width}x{self.height}")
        except ValueError:
            print("❌ Valor inválido. Manteniendo tamaño actual.")
    
    def get_parking_spaces(self) -> List[ParkingSpace]:
        """Convierte las posiciones a objetos ParkingSpace"""
        spaces = []
        for i, (x, y) in enumerate(self.pos_list):
            space = ParkingSpace(
                x=x, y=y, 
                width=self.width, height=self.height,
                id=f"legacy_space_{i}",
                confidence=1.0
            )
            spaces.append(space)
        return spaces

class LegacyOccupancyDetector:
    """Detector de ocupación basado en el código original mejorado"""
    
    def __init__(self):
        self.threshold = 900  # Umbral para determinar ocupación
        self.width = 107
        self.height = 48
        
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocesa el frame usando las técnicas del código original"""
        # Convertir a escala de grises
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Aplicar desenfoque gaussiano
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        
        # Umbralización adaptativa
        img_threshold = cv2.adaptiveThreshold(
            img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 25, 16
        )
        
        # Filtro de mediana
        img_median = cv2.medianBlur(img_threshold, 5)
        
        # Dilatación morfológica
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_median, kernel, iterations=1)
        
        return img_dilate
    
    def check_parking_spaces(self, frame: np.ndarray, spaces: List[ParkingSpace]) -> Tuple[List[OccupancyStatus], int]:
        """Verifica la ocupación de los espacios usando el algoritmo original"""
        processed_frame = self.preprocess_frame(frame)
        results = []
        free_count = 0
        
        for space in spaces:
            # Extraer región de interés
            img_crop = processed_frame[space.y:space.y + space.height, 
                                     space.x:space.x + space.width]
            
            if img_crop.size == 0:
                continue
            
            # Contar píxeles no-cero
            count = cv2.countNonZero(img_crop)
            
            # Determinar ocupación
            is_occupied = count >= self.threshold
            confidence = min(count / 1500, 1.0)  # Normalizar confianza
            
            if not is_occupied:
                free_count += 1
                color = (0, 255, 0)  # Verde para libre
                thickness = 5
            else:
                color = (0, 0, 255)  # Rojo para ocupado
                thickness = 2
            
            # Dibujar rectángulo en el frame original
            cv2.rectangle(frame, (space.x, space.y), 
                         (space.x + space.width, space.y + space.height), 
                         color, thickness)
            
            # Mostrar conteo de píxeles con cvzone si está disponible
            if CVZONE_AVAILABLE:
                cvzone.putTextRect(frame, str(count), 
                                 (space.x, space.y + space.height - 3), 
                                 scale=1, thickness=2, offset=0, colorR=color)
            else:
                # Fallback sin cvzone
                cv2.putText(frame, str(count), 
                          (space.x, space.y + space.height - 3),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Crear estado de ocupación
            status = OccupancyStatus(
                space_id=space.id or f"space_{id(space)}",
                is_occupied=is_occupied,
                confidence=confidence,
                timestamp=datetime.now().isoformat()
            )
            results.append(status)
        
        # Mostrar resumen
        total_spaces = len(spaces)
        if CVZONE_AVAILABLE:
            cvzone.putTextRect(frame, f'Libres: {free_count}/{total_spaces}', 
                             (100, 50), scale=3, thickness=5, offset=20, 
                             colorR=(0, 200, 0))
        else:
            cv2.putText(frame, f'Libres: {free_count}/{total_spaces}', 
                       (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                       (0, 200, 0), 3)
        
        return results, free_count

class LegacyVideoProcessor:
    """Procesador de video basado en el código original mejorado"""
    
    def __init__(self, video_path: str, positions_file: str = "CarParkPos"):
        self.video_path = video_path
        self.positions_file = positions_file
        self.cap = None
        self.detector = LegacyOccupancyDetector()
        self.spaces = []
        self.is_playing = False
        
        # Cargar espacios
        self.load_spaces()
    
    def load_spaces(self):
        """Carga los espacios desde el archivo de posiciones"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'rb') as f:
                    pos_list = pickle.load(f)
                
                self.spaces = []
                for i, (x, y) in enumerate(pos_list):
                    space = ParkingSpace(
                        x=x, y=y, 
                        width=107, height=48,  # Valores por defecto
                        id=f"video_space_{i}",
                        confidence=1.0
                    )
                    self.spaces.append(space)
                
                print(f"✅ Cargados {len(self.spaces)} espacios para análisis de video")
            else:
                print(f"❌ Archivo {self.positions_file} no encontrado")
        except Exception as e:
            print(f"❌ Error cargando espacios: {e}")
    
    def play_video(self):
        """Reproduce el video con detección de ocupación"""
        if not os.path.exists(self.video_path):
            print(f"❌ Video no encontrado: {self.video_path}")
            return
        
        if not self.spaces:
            print("❌ No hay espacios definidos. Usa el editor primero.")
            return
        
        self.cap = cv2.VideoCapture(self.video_path)
        
        if not self.cap.isOpened():
            print(f"❌ No se pudo abrir el video: {self.video_path}")
            return
        
        self.is_playing = True
        print("🎬 Reproduciendo video con detección:")
        print("   • Tecla 'q': Salir")
        print("   • Tecla ESPACIO: Pausar/Reanudar")
        print("   • Tecla 'r': Reiniciar video")
        
        paused = False
        
        while self.is_playing:
            if not paused:
                # Verificar si llegamos al final del video
                if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reiniciar
                
                success, frame = self.cap.read()
                if not success:
                    print("❌ Error leyendo frame del video")
                    break
                
                # Analizar ocupación
                results, free_count = self.detector.check_parking_spaces(frame, self.spaces)
                
                # Mostrar frame
                cv2.imshow("CarPark - Detección en Video", frame)
            
            # Manejar teclas
            key = cv2.waitKey(30 if not paused else 1) & 0xFF
            if key == ord('q'):
                self.is_playing = False
            elif key == ord(' '):  # Espacio para pausar/reanudar
                paused = not paused
                print(f"⏸️  Video {'pausado' if paused else 'reanudado'}")
            elif key == ord('r'):  # Reiniciar video
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                print("🔄 Video reiniciado")
        
        # Limpiar
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Reproducción finalizada")
