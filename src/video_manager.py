"""
Gestión de video y captura de frames
"""
import cv2
import numpy as np
from typing import Optional, Tuple, Callable
import threading
import time

class VideoManager:
    """Maneja la captura y reproducción de video"""
    
    def __init__(self):
        self.cap = None
        self.is_paused = True
        self.current_frame = None
        self.video_path = None
        self.frame_callback: Optional[Callable] = None
        self._thread = None
        self._stop_event = threading.Event()
        
    def load_video(self, path: str) -> bool:
        """Carga un archivo de video"""
        try:
            if self.cap:
                self.cap.release()
            
            self.cap = cv2.VideoCapture(path)
            if not self.cap.isOpened():
                return False
                
            self.video_path = path
            # Leer primer frame
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
            return True
        except Exception as e:
            print(f"Error cargando video: {e}")
            return False
    
    def load_camera(self, camera_index: int = 0) -> bool:
        """Carga una cámara"""
        try:
            if self.cap:
                self.cap.release()
                
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                return False
                
            self.video_path = f"Camera_{camera_index}"
            return True
        except Exception as e:
            print(f"Error cargando cámara: {e}")
            return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Obtiene el frame actual"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
                return frame
        return self.current_frame
    
    def start_capture(self, callback: Callable = None):
        """Inicia la captura continua"""
        if callback:
            self.frame_callback = callback
        
        if self._thread and self._thread.is_alive():
            return
            
        self.is_paused = False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._capture_loop)
        self._thread.daemon = True
        self._thread.start()
    
    def pause_capture(self):
        """Pausa la captura"""
        self.is_paused = True
    
    def resume_capture(self):
        """Reanuda la captura"""
        self.is_paused = False
    
    def stop_capture(self):
        """Detiene la captura"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)
    
    def _capture_loop(self):
        """Loop principal de captura"""
        while not self._stop_event.is_set():
            if not self.is_paused and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame.copy()
                    if self.frame_callback:
                        self.frame_callback(frame)
                else:
                    # Si el video terminó, reiniciar
                    if self.video_path and not self.video_path.startswith("Camera_"):
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            time.sleep(0.033)  # ~30 FPS
    
    def get_video_info(self) -> dict:
        """Obtiene información del video"""
        if not self.cap:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'current_frame': int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        }
    
    def seek_frame(self, frame_number: int):
        """Salta a un frame específico"""
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    def release(self):
        """Libera recursos"""
        self.stop_capture()
        if self.cap:
            self.cap.release()
            self.cap = None
