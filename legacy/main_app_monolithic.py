import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import threading
import numpy as np
import pickle
import os
import time
import csv
from datetime import datetime
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any

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

class VideoManager:
    """Maneja la captura y reproducción de video"""
    
    def __init__(self):
        self.cap = None
        self.is_paused = True
        self.current_frame = None
        self.video_path = None
        
    def load_video(self, path: str) -> bool:
        """Carga un archivo de video"""
        try:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(path)
            self.video_path = path
            return self.cap.isOpened()
        except Exception as e:
            print(f"Error cargando video: {e}")
            return False
    
    def start_camera(self, device_id: int = 0) -> bool:
        """Inicia la cámara"""
        try:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(device_id)
            self.video_path = f"camera_{device_id}"
            return self.cap.isOpened()
        except Exception as e:
            print(f"Error iniciando cámara: {e}")
            return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Obtiene el frame actual"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame.copy()
                return frame
        return None
    
    def capture_current_frame(self) -> Optional[np.ndarray]:
        """Captura y pausa en el frame actual"""
        frame = self.get_frame()
        if frame is not None:
            self.is_paused = True
            return frame
        return None
    
    def release(self):
        """Libera recursos"""
        if self.cap:
            self.cap.release()
            self.cap = None

class SmartDetector:
    """Detector inteligente de espacios de estacionamiento mejorado"""
    
    def __init__(self):
        self.min_area = 1500
        self.max_area = 15000
        self.aspect_ratio_min = 0.8
        self.aspect_ratio_max = 3.5
        self.merge_distance = 30
        
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Preprocesamiento avanzado de imagen"""
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Ecualización adaptativa de histograma
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Filtro bilateral para reducir ruido manteniendo bordes
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        return gray
    
    def detect_edges(self, gray: np.ndarray) -> np.ndarray:
        """Detección de bordes mejorada"""
        # Gradient magnitude usando Sobel
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(grad_x**2 + grad_y**2)
        magnitude = np.uint8(magnitude / magnitude.max() * 255)
        
        # Canny con umbral adaptativo
        median_val = float(np.median(gray))
        lower = int(max(0, 0.7 * median_val))
        upper = int(min(255, 1.3 * median_val))
        edges = cv2.Canny(gray, lower, upper)
        
        # Combinación de ambos
        combined = cv2.bitwise_or(edges, cv2.threshold(magnitude, 50, 255, cv2.THRESH_BINARY)[1])
        
        return combined
    
    def find_rectangular_contours(self, edges: np.ndarray) -> List[np.ndarray]:
        """Encuentra contornos rectangulares"""
        # Operaciones morfológicas para conectar líneas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangular_contours = []
        for contour in contours:
            # Aproximación poligonal
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Filtrar por número de vértices (cuadriláteros)
            if len(approx) >= 4:
                rectangular_contours.append(contour)
        
        return rectangular_contours
    
    def validate_parking_space(self, contour: np.ndarray) -> Optional[ParkingSpace]:
        """Valida si un contorno es un espacio de estacionamiento válido"""
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = max(w, h) / min(w, h)
        
        # Filtros de validación
        if area < self.min_area or area > self.max_area:
            return None
        
        if aspect_ratio < self.aspect_ratio_min or aspect_ratio > self.aspect_ratio_max:
            return None
        
        # Calcular confianza basada en múltiples factores
        contour_area = cv2.contourArea(contour)
        fill_ratio = contour_area / area if area > 0 else 0
        confidence = fill_ratio * 0.6 + (1 / aspect_ratio) * 0.4
        
        return ParkingSpace(x, y, w, h, confidence=confidence)
    
    def cluster_and_merge_spaces(self, spaces: List[ParkingSpace]) -> List[ParkingSpace]:
        """Agrupa y fusiona espacios cercanos"""
        if not spaces:
            return []
        
        merged = []
        used = set()
        
        for i, space1 in enumerate(spaces):
            if i in used:
                continue
                
            cluster = [space1]
            used.add(i)
            
            for j, space2 in enumerate(spaces[i+1:], i+1):
                if j in used:
                    continue
                    
                # Calcular distancia entre centros
                center1 = space1.center
                center2 = space2.center
                distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
                
                if distance < self.merge_distance:
                    cluster.append(space2)
                    used.add(j)
            
            # Fusionar cluster en un solo espacio
            if len(cluster) == 1:
                merged.append(cluster[0])
            else:
                merged_space = self.merge_cluster(cluster)
                if merged_space:
                    merged.append(merged_space)
        
        return merged
    
    def merge_cluster(self, cluster: List[ParkingSpace]) -> Optional[ParkingSpace]:
        """Fusiona un cluster de espacios en uno solo"""
        if not cluster:
            return None
        
        min_x = min(space.x for space in cluster)
        min_y = min(space.y for space in cluster)
        max_x = max(space.x + space.width for space in cluster)
        max_y = max(space.y + space.height for space in cluster)
        
        width = max_x - min_x
        height = max_y - min_y
        avg_confidence = sum(space.confidence for space in cluster) / len(cluster)
        
        return ParkingSpace(min_x, min_y, width, height, confidence=avg_confidence)
    
    def organize_in_grid(self, spaces: List[ParkingSpace]) -> List[ParkingSpace]:
        """Organiza espacios en una grilla lógica"""
        if not spaces:
            return []
        
        # Agrupar por filas (Y similar)
        tolerance = 30
        rows = {}
        
        for space in spaces:
            row_found = False
            for row_y in rows.keys():
                if abs(space.y - row_y) <= tolerance:
                    rows[row_y].append(space)
                    row_found = True
                    break
            
            if not row_found:
                rows[space.y] = [space]
        
        # Ordenar cada fila por X y normalizar dimensiones
        organized = []
        for row_y in sorted(rows.keys()):
            row_spaces = sorted(rows[row_y], key=lambda s: s.x)
            
            # Calcular dimensiones promedio de la fila
            avg_width = int(np.median([s.width for s in row_spaces]))
            avg_height = int(np.median([s.height for s in row_spaces]))
            
            # Normalizar espacios de la fila
            for space in row_spaces:
                normalized = ParkingSpace(
                    space.x, row_y, avg_width, avg_height,
                    confidence=space.confidence
                )
                organized.append(normalized)
        
        return organized
    
    def detect_parking_spaces(self, img: np.ndarray) -> List[ParkingSpace]:
        """Detecta espacios de estacionamiento de forma inteligente"""
        # Preprocesamiento
        gray = self.preprocess_image(img)
        
        # Detección de bordes
        edges = self.detect_edges(gray)
        
        # Encontrar contornos rectangulares
        contours = self.find_rectangular_contours(edges)
        
        # Validar espacios
        candidate_spaces = []
        for contour in contours:
            space = self.validate_parking_space(contour)
            if space:
                candidate_spaces.append(space)
        
        # Agrupar y fusionar espacios cercanos
        merged_spaces = self.cluster_and_merge_spaces(candidate_spaces)
        
        # Organizar en grilla
        organized_spaces = self.organize_in_grid(merged_spaces)
        
        # Filtrar por confianza
        final_spaces = [s for s in organized_spaces if s.confidence > 0.3]
        
        return final_spaces

class OccupancyAnalyzer:
    """Analizador de ocupación mejorado"""
    
    def __init__(self):
        self.threshold_method = 'adaptive'  # 'fixed', 'adaptive', 'ml'
        self.fixed_threshold = 120
        
    def analyze_space_occupancy(self, img: np.ndarray, space: ParkingSpace) -> bool:
        """Analiza si un espacio está ocupado"""
        # Extraer región del espacio
        roi = img[space.y:space.y + space.height, space.x:space.x + space.width]
        
        if roi.size == 0:
            return False
        
        # Convertir a escala de grises si es necesario
        if len(roi.shape) == 3:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            roi_gray = roi
        
        if self.threshold_method == 'adaptive':
            return self._adaptive_threshold_analysis(roi_gray)
        elif self.threshold_method == 'ml':
            return self._ml_based_analysis(roi_gray)
        else:
            return self._fixed_threshold_analysis(roi_gray)
    
    def _fixed_threshold_analysis(self, roi: np.ndarray) -> bool:
        """Análisis con umbral fijo"""
        mean_intensity = np.mean(roi)
        return bool(mean_intensity < self.fixed_threshold)
    
    def _adaptive_threshold_analysis(self, roi: np.ndarray) -> bool:
        """Análisis con umbral adaptativo"""
        # Calcular estadísticas de la ROI
        mean_intensity = np.mean(roi)
        std_intensity = np.std(roi)
        
        # Detectar bordes para medir textura
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calcular umbral adaptativo basado en la imagen completa
        global_mean = np.mean(roi)
        adaptive_threshold = global_mean * 0.8
        
        # Combinar criterios
        is_dark = mean_intensity < adaptive_threshold
        has_texture = edge_density > 0.02
        has_variation = std_intensity > 15
        
        # Un espacio está ocupado si es oscuro Y (tiene textura O variación)
        return bool(is_dark and (has_texture or has_variation))
    
    def _ml_based_analysis(self, roi: np.ndarray) -> bool:
        """Análisis basado en características de ML (simplificado)"""
        # Extraer características
        features = self._extract_features(roi)
        
        # Clasificación simple basada en reglas (se puede reemplazar con ML real)
        score = (
            features['darkness'] * 0.4 +
            features['texture'] * 0.3 +
            features['edges'] * 0.3
        )
        
        return score > 0.5
    
    def _extract_features(self, roi: np.ndarray) -> Dict[str, float]:
        """Extrae características para análisis ML"""
        # Normalizar ROI
        roi_norm = roi / 255.0
        
        # Características de intensidad
        mean_intensity = np.mean(roi_norm)
        std_intensity = np.std(roi_norm)
        
        # Características de textura (LBP simplificado)
        texture_score = std_intensity / (mean_intensity + 0.001)
        
        # Características de bordes
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        return {
            'darkness': float(1.0 - mean_intensity),
            'texture': float(min(float(texture_score), 1.0)),
            'edges': float(edge_density),
            'variation': float(min(float(std_intensity) * 2, 1.0))
        }

class CarParkAppRefactored:
    """Aplicación principal refactorizada"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Componentes principales
        self.video_manager = VideoManager()
        self.detector = SmartDetector()
        self.analyzer = OccupancyAnalyzer()
        
        # Estado de la aplicación
        self.current_image = None
        self.parking_spaces: List[ParkingSpace] = []
        self.analysis_results: List[bool] = []
        self.analysis_history: List[Dict] = []
        
        # Estado de la interfaz
        self.selected_space = None
        self.is_analyzing = False
        self.analysis_mode = False
        self.drawing_mode = False
        self.rect_start = None
        self.rect_preview = None
        
        # Crear interfaz
        self.create_interface()
        self.bind_events()
        self.start_update_loop()
    
    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title("CarPark Project - Refactorizado v2.0")
        self.root.geometry("1400x900")
        self.root.configure(bg="#2b2b2b")
        
    def create_interface(self):
        """Crea la interfaz de usuario"""
        # Panel principal
        main_frame = tk.Frame(self.root, bg="#2b2b2b")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel de control (izquierda)
        self.create_control_panel(main_frame)
        
        # Panel de visualización (centro/derecha)
        self.create_display_panel(main_frame)
        
        # Barra de estado
        self.create_status_bar()
    
    def create_control_panel(self, parent):
        """Crea el panel de controles"""
        control_frame = tk.Frame(parent, bg="#3b3b3b", width=350)
        control_frame.pack(side="left", fill="y", padx=(0, 10))
        control_frame.pack_propagate(False)
        
        # Título
        title_label = tk.Label(control_frame, text="CarPark Control", 
                              font=("Arial", 16, "bold"), fg="white", bg="#3b3b3b")
        title_label.pack(pady=10)
        
        # Sección: Fuente de video
        self.create_video_section(control_frame)
        
        # Sección: Detección
        self.create_detection_section(control_frame)
        
        # Sección: Análisis
        self.create_analysis_section(control_frame)
        
        # Sección: Estadísticas
        self.create_stats_section(control_frame)
        
        # Sección: Configuración
        self.create_config_section(control_frame)
    
    def create_video_section(self, parent):
        """Crea la sección de video"""
        section = self.create_section(parent, "📹 Fuente de Video")
        
        # Botones de carga
        btn_frame = tk.Frame(section, bg="#3b3b3b")
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="📁 Cargar Video", command=self.load_video,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=2)
        
        tk.Button(btn_frame, text="📷 Usar Cámara", command=self.start_camera,
                 bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=2)
        
        # Controles de video
        video_controls = tk.Frame(section, bg="#3b3b3b")
        video_controls.pack(fill="x", pady=5)
        
        tk.Button(video_controls, text="⏯️", command=self.toggle_video,
                 bg="#FF9800", fg="white", width=5).pack(side="left", padx=2)
        
        tk.Button(video_controls, text="📸", command=self.capture_frame,
                 bg="#9C27B0", fg="white", width=5).pack(side="left", padx=2)
    
    def create_detection_section(self, parent):
        """Crea la sección de detección"""
        section = self.create_section(parent, "🔍 Detección de Espacios")
        
        tk.Button(section, text="🤖 Detección Automática Inteligente", 
                 command=self.smart_auto_detection,
                 bg="#FF5722", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=2)
        
        tk.Button(section, text="✏️ Definir Manualmente", 
                 command=self.toggle_manual_mode,
                 bg="#795548", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=2)
        
        # Configuración de detector
        config_frame = tk.Frame(section, bg="#3b3b3b")
        config_frame.pack(fill="x", pady=5)
        
        tk.Label(config_frame, text="Sensibilidad:", fg="white", bg="#3b3b3b").pack(anchor="w")
        self.sensitivity_var = tk.DoubleVar(value=0.5)
        tk.Scale(config_frame, from_=0.1, to=1.0, resolution=0.1, orient="horizontal",
                variable=self.sensitivity_var, bg="#3b3b3b", fg="white").pack(fill="x")
    
    def create_analysis_section(self, parent):
        """Crea la sección de análisis"""
        section = self.create_section(parent, "📊 Análisis de Ocupación")
        
        tk.Button(section, text="▶️ Iniciar Análisis", 
                 command=self.start_occupancy_analysis,
                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(fill="x", pady=5)
        
        tk.Button(section, text="⏹️ Detener Análisis", 
                 command=self.stop_analysis,
                 bg="#F44336", fg="white", font=("Arial", 12, "bold")).pack(fill="x", pady=2)
        
        # Método de análisis
        method_frame = tk.Frame(section, bg="#3b3b3b")
        method_frame.pack(fill="x", pady=5)
        
        tk.Label(method_frame, text="Método:", fg="white", bg="#3b3b3b").pack(anchor="w")
        self.analysis_method = tk.StringVar(value="adaptive")
        methods = [("Umbral Fijo", "fixed"), ("Adaptativo", "adaptive"), ("ML Avanzado", "ml")]
        
        for text, value in methods:
            tk.Radiobutton(method_frame, text=text, variable=self.analysis_method, 
                          value=value, fg="white", bg="#3b3b3b", 
                          selectcolor="#555").pack(anchor="w")
    
    def create_stats_section(self, parent):
        """Crea la sección de estadísticas"""
        section = self.create_section(parent, "📈 Estadísticas en Tiempo Real")
        
        # Labels de estadísticas
        self.stats_frame = tk.Frame(section, bg="#3b3b3b")
        self.stats_frame.pack(fill="x", pady=5)
        
        self.libre_label = tk.Label(self.stats_frame, text="🟢 Libres: -", 
                                   fg="#4CAF50", bg="#3b3b3b", font=("Arial", 12, "bold"))
        self.libre_label.pack(anchor="w")
        
        self.ocupado_label = tk.Label(self.stats_frame, text="🔴 Ocupados: -", 
                                     fg="#F44336", bg="#3b3b3b", font=("Arial", 12, "bold"))
        self.ocupado_label.pack(anchor="w")
        
        self.total_label = tk.Label(self.stats_frame, text="📊 Total: -", 
                                   fg="white", bg="#3b3b3b", font=("Arial", 12, "bold"))
        self.total_label.pack(anchor="w")
        
        self.efficiency_label = tk.Label(self.stats_frame, text="⚡ Eficiencia: -", 
                                        fg="#FF9800", bg="#3b3b3b", font=("Arial", 12, "bold"))
        self.efficiency_label.pack(anchor="w")
    
    def create_config_section(self, parent):
        """Crea la sección de configuración"""
        section = self.create_section(parent, "⚙️ Configuración")
        
        # Botones de archivos
        file_frame = tk.Frame(section, bg="#3b3b3b")
        file_frame.pack(fill="x", pady=5)
        
        tk.Button(file_frame, text="💾 Guardar Espacios", command=self.save_spaces,
                 bg="#607D8B", fg="white").pack(fill="x", pady=1)
        
        tk.Button(file_frame, text="📂 Cargar Espacios", command=self.load_spaces,
                 bg="#607D8B", fg="white").pack(fill="x", pady=1)
        
        tk.Button(file_frame, text="📋 Exportar Resultados", command=self.export_results,
                 bg="#607D8B", fg="white").pack(fill="x", pady=1)
        
        tk.Button(file_frame, text="🔄 Reiniciar Todo", command=self.reset_all,
                 bg="#795548", fg="white").pack(fill="x", pady=1)
    
    def create_section(self, parent, title):
        """Crea una sección con título"""
        section_frame = tk.Frame(parent, bg="#3b3b3b", relief="raised", bd=1)
        section_frame.pack(fill="x", pady=5, padx=5)
        
        title_label = tk.Label(section_frame, text=title, 
                              font=("Arial", 11, "bold"), fg="#FFF", bg="#444")
        title_label.pack(fill="x", pady=2)
        
        content_frame = tk.Frame(section_frame, bg="#3b3b3b")
        content_frame.pack(fill="x", padx=5, pady=5)
        
        return content_frame
    
    def create_display_panel(self, parent):
        """Crea el panel de visualización"""
        display_frame = tk.Frame(parent, bg="#2b2b2b")
        display_frame.pack(side="right", fill="both", expand=True)
        
        # Canvas para la imagen
        self.canvas = tk.Canvas(display_frame, bg="black", width=1000, height=750)
        self.canvas.pack(padx=10, pady=10)
        
        # Panel de herramientas de edición
        tools_frame = tk.Frame(display_frame, bg="#3b3b3b")
        tools_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(tools_frame, text="🖱️ Seleccionar", command=lambda: self.set_tool('select'),
                 bg="#455A64", fg="white").pack(side="left", padx=2)
        
        tk.Button(tools_frame, text="✏️ Dibujar", command=lambda: self.set_tool('draw'),
                 bg="#455A64", fg="white").pack(side="left", padx=2)
        
        tk.Button(tools_frame, text="🗑️ Eliminar", command=self.delete_selected,
                 bg="#455A64", fg="white").pack(side="left", padx=2)
    
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_bar = tk.Label(self.root, text="Listo", relief="sunken", anchor="w",
                                  bg="#333", fg="white", font=("Arial", 9))
        self.status_bar.pack(side="bottom", fill="x")
    
    def bind_events(self):
        """Vincula eventos de la interfaz"""
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        
        # Atajos de teclado
        self.root.bind("<Control-s>", lambda e: self.save_spaces())
        self.root.bind("<Control-o>", lambda e: self.load_spaces())
        self.root.bind("<Control-n>", lambda e: self.reset_all())
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<Escape>", lambda e: self.clear_selection())
    
    def set_status(self, message: str):
        """Actualiza la barra de estado"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    # Métodos de video
    def load_video(self):
        """Carga un archivo de video"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=[("Videos", "*.mp4 *.avi *.mov *.mkv"), ("Todos", "*.*")]
        )
        
        if file_path:
            if self.video_manager.load_video(file_path):
                self.set_status(f"Video cargado: {os.path.basename(file_path)}")
                self.video_manager.is_paused = False
            else:
                messagebox.showerror("Error", "No se pudo cargar el video")
    
    def start_camera(self):
        """Inicia la cámara"""
        if self.video_manager.start_camera():
            self.set_status("Cámara iniciada")
            self.video_manager.is_paused = False
        else:
            messagebox.showerror("Error", "No se pudo iniciar la cámara")
    
    def toggle_video(self):
        """Alterna pausa/reproducción del video"""
        self.video_manager.is_paused = not self.video_manager.is_paused
        status = "pausado" if self.video_manager.is_paused else "reproduciendo"
        self.set_status(f"Video {status}")
    
    def capture_frame(self):
        """Captura el frame actual"""
        frame = self.video_manager.capture_current_frame()
        if frame is not None:
            self.current_image = frame
            self.set_status("Frame capturado - Listo para detección")
        else:
            messagebox.showwarning("Advertencia", "No hay video activo para capturar")
    
    # Métodos de detección
    def smart_auto_detection(self):
        """Ejecuta detección automática inteligente"""
        if self.current_image is None:
            messagebox.showwarning("Advertencia", "Carga una imagen o captura un frame primero")
            return
        
        self.set_status("Detectando espacios...")
        
        # Configurar detector según sensibilidad
        sensitivity = self.sensitivity_var.get()
        self.detector.min_area = int(1000 * sensitivity)
        self.detector.max_area = int(20000 * sensitivity)
        
        # Ejecutar detección en hilo separado
        def detect():
            try:
                if self.current_image is not None:
                    detected_spaces = self.detector.detect_parking_spaces(self.current_image)
                    # Actualizar en hilo principal
                    self.root.after(0, lambda: self.on_detection_complete(detected_spaces))
                else:
                    self.root.after(0, lambda: self.on_detection_error("No hay imagen disponible"))
                
            except Exception as e:
                self.root.after(0, lambda: self.on_detection_error(str(e)))
        
        threading.Thread(target=detect, daemon=True).start()
    
    def on_detection_complete(self, spaces: List[ParkingSpace]):
        """Maneja la finalización de la detección"""
        self.parking_spaces = spaces
        count = len(spaces)
        self.set_status(f"Detección completada: {count} espacios encontrados")
        self.update_stats_display()
        
        if count == 0:
            messagebox.showinfo("Resultado", "No se detectaron espacios de estacionamiento.\n"
                                           "Intenta ajustar la sensibilidad o usar detección manual.")
        else:
            messagebox.showinfo("Éxito", f"Se detectaron {count} espacios de estacionamiento.\n"
                                        "Puedes editarlos manualmente si es necesario.")
    
    def on_detection_error(self, error: str):
        """Maneja errores de detección"""
        self.set_status("Error en detección")
        messagebox.showerror("Error de Detección", f"Ocurrió un error:\n{error}")
    
    def toggle_manual_mode(self):
        """Alterna modo de dibujo manual"""
        self.drawing_mode = not self.drawing_mode
        mode = "activado" if self.drawing_mode else "desactivado"
        self.set_status(f"Modo dibujo manual {mode}")
    
    # Métodos de análisis
    def start_occupancy_analysis(self):
        """Inicia análisis de ocupación"""
        if not self.parking_spaces:
            messagebox.showwarning("Advertencia", "Primero define los espacios de estacionamiento")
            return
        
        if self.current_image is None:
            # Capturar frame actual si hay video
            frame = self.video_manager.capture_current_frame()
            if frame is not None:
                self.current_image = frame
            else:
                messagebox.showwarning("Advertencia", "No hay imagen para analizar")
                return
        
        self.is_analyzing = True
        self.analysis_mode = True
        self.set_status("Analizando ocupación...")
        
        # Configurar analizador
        self.analyzer.threshold_method = self.analysis_method.get()
        
        # Ejecutar análisis en hilo separado
        def analyze():
            try:
                if self.current_image is None:
                    self.root.after(0, lambda: self.on_analysis_error("No hay imagen disponible"))
                    return
                
                results = []
                for i, space in enumerate(self.parking_spaces):
                    # Actualizar progreso
                    progress = f"Analizando espacio {i+1}/{len(self.parking_spaces)}"
                    self.root.after(0, lambda p=progress: self.set_status(p))
                    
                    # Analizar ocupación
                    is_occupied = self.analyzer.analyze_space_occupancy(self.current_image, space)
                    results.append(is_occupied)
                    
                    time.sleep(0.05)  # Pequeña pausa para visualizar progreso
                
                # Actualizar resultados en hilo principal
                self.root.after(0, lambda: self.on_analysis_complete(results))
                
            except Exception as e:
                self.root.after(0, lambda: self.on_analysis_error(str(e)))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def on_analysis_complete(self, results: List[bool]):
        """Maneja la finalización del análisis"""
        self.analysis_results = results
        self.is_analyzing = False
        
        # Calcular estadísticas
        occupied = sum(results)
        free = len(results) - occupied
        total = len(results)
        efficiency = (free / total * 100) if total > 0 else 0
        
        # Guardar en historial
        timestamp = datetime.now()
        self.analysis_history.append({
            'timestamp': timestamp,
            'total': total,
            'occupied': occupied,
            'free': free,
            'efficiency': efficiency
        })
        
        self.update_stats_display()
        self.set_status(f"Análisis completado: {free} libres, {occupied} ocupados")
        
        # Mostrar resultados
        messagebox.showinfo("Análisis Completado", 
                           f"Resultados del análisis:\n\n"
                           f"🟢 Espacios libres: {free}\n"
                           f"🔴 Espacios ocupados: {occupied}\n"
                           f"📊 Total: {total}\n"
                           f"⚡ Eficiencia: {efficiency:.1f}%")
    
    def on_analysis_error(self, error: str):
        """Maneja errores de análisis"""
        self.is_analyzing = False
        self.analysis_mode = False
        self.set_status("Error en análisis")
        messagebox.showerror("Error de Análisis", f"Ocurrió un error:\n{error}")
    
    def stop_analysis(self):
        """Detiene el análisis"""
        if not self.analysis_mode and not self.is_analyzing:
            messagebox.showinfo("Info", "No hay análisis activo")
            return
        
        self.analysis_mode = False
        self.is_analyzing = False
        
        # Preguntar sobre reanudar video
        if self.video_manager.cap and self.video_manager.is_paused:
            if messagebox.askyesno("Reanudar Video", "¿Reanudar reproducción del video?"):
                self.video_manager.is_paused = False
        
        self.set_status("Análisis detenido - Modo edición activado")
    
    def update_stats_display(self):
        """Actualiza la visualización de estadísticas"""
        if self.analysis_results:
            occupied = sum(self.analysis_results)
            free = len(self.analysis_results) - occupied
            total = len(self.analysis_results)
            efficiency = (free / total * 100) if total > 0 else 0
            
            self.libre_label.config(text=f"🟢 Libres: {free}")
            self.ocupado_label.config(text=f"🔴 Ocupados: {occupied}")
            self.total_label.config(text=f"📊 Total: {total}")
            self.efficiency_label.config(text=f"⚡ Eficiencia: {efficiency:.1f}%")
        else:
            spaces_count = len(self.parking_spaces)
            self.libre_label.config(text="🟢 Libres: -")
            self.ocupado_label.config(text="🔴 Ocupados: -")
            self.total_label.config(text=f"📊 Espacios definidos: {spaces_count}")
            self.efficiency_label.config(text="⚡ Eficiencia: -")
    
    # Métodos de interfaz
    def update_canvas(self):
        """Actualiza el canvas con la imagen actual"""
        # Obtener frame del video si no está en modo análisis
        if (self.video_manager.cap and not self.video_manager.is_paused 
            and not self.analysis_mode):
            frame = self.video_manager.get_frame()
            if frame is not None:
                self.current_image = frame
        
        if self.current_image is not None:
            # Crear copia para dibujar
            display_img = self.current_image.copy()
            
            # Dibujar espacios de estacionamiento
            self.draw_parking_spaces(display_img)
            
            # Dibujar indicadores especiales
            if self.analysis_mode:
                self.draw_analysis_overlay(display_img)
            
            if self.rect_preview:
                self.draw_preview_rect(display_img)
            
            # Convertir y mostrar en canvas
            self.display_image_on_canvas(display_img)
    
    def draw_parking_spaces(self, img: np.ndarray):
        """Dibuja los espacios de estacionamiento en la imagen"""
        for i, space in enumerate(self.parking_spaces):
            # Determinar color
            if self.analysis_results and i < len(self.analysis_results):
                color = (0, 0, 255) if self.analysis_results[i] else (0, 255, 0)
                thickness = 3
            else:
                color = (255, 255, 0) if i != self.selected_space else (0, 255, 255)
                thickness = 2
            
            # Dibujar rectángulo
            cv2.rectangle(img, (space.x, space.y), 
                         (space.x + space.width, space.y + space.height), 
                         color, thickness)
            
            # Dibujar número
            text = str(i + 1)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            text_x = space.x + (space.width - text_size[0]) // 2
            text_y = space.y + (space.height + text_size[1]) // 2
            
            # Fondo para el texto
            cv2.rectangle(img, (text_x - 5, text_y - text_size[1] - 5),
                         (text_x + text_size[0] + 5, text_y + 5), (0, 0, 0), -1)
            cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                       (255, 255, 255), 2)
            
            # Mostrar confianza si está disponible
            if hasattr(space, 'confidence') and space.confidence > 0:
                conf_text = f"{space.confidence:.2f}"
                cv2.putText(img, conf_text, (space.x, space.y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def draw_analysis_overlay(self, img: np.ndarray):
        """Dibuja overlay de modo análisis"""
        # Texto de modo análisis
        text = "MODO ANÁLISIS - Frame Capturado"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        
        # Fondo semi-transparente
        overlay = img.copy()
        cv2.rectangle(overlay, (10, 10), (text_size[0] + 40, text_size[1] + 40), 
                     (0, 0, 255), -1)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        
        # Texto
        cv2.putText(img, text, (25, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, 
                   (255, 255, 255), 2)
    
    def draw_preview_rect(self, img: np.ndarray):
        """Dibuja rectángulo de previsualización"""
        if self.rect_preview:
            x, y, w, h = self.rect_preview
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    def display_image_on_canvas(self, img: np.ndarray):
        """Muestra imagen en el canvas"""
        # Redimensionar para ajustar al canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:
            # Convertir a RGB y redimensionar
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_resized = img_pil.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            # Convertir a ImageTk
            self.canvas_image = ImageTk.PhotoImage(img_resized)
            
            # Mostrar en canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                   image=self.canvas_image)
    
    def start_update_loop(self):
        """Inicia el bucle de actualización"""
        self.update_canvas()
        self.root.after(33, self.start_update_loop)  # ~30 FPS
    
    # Métodos de eventos del canvas
    def on_canvas_click(self, event):
        """Maneja clic en canvas"""
        if self.current_image is None:
            return
        
        # Convertir coordenadas del canvas a imagen
        x, y = self.canvas_to_image_coords(event.x, event.y)
        
        if self.drawing_mode:
            self.start_drawing_rect(x, y)
        else:
            self.select_space_at_point(x, y)
    
    def on_canvas_drag(self, event):
        """Maneja arrastrar en canvas"""
        if self.drawing_mode and self.rect_start:
            x, y = self.canvas_to_image_coords(event.x, event.y)
            self.update_preview_rect(x, y)
    
    def on_canvas_release(self, event):
        """Maneja soltar botón del mouse"""
        if self.drawing_mode and self.rect_preview:
            self.finish_drawing_rect()
    
    def on_canvas_right_click(self, event):
        """Maneja clic derecho en canvas"""
        # Menú contextual
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Eliminar selección", command=self.delete_selected)
        menu.add_command(label="Duplicar espacio", command=self.duplicate_selected)
        menu.add_separator()
        menu.add_command(label="Propiedades", command=self.show_space_properties)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def canvas_to_image_coords(self, canvas_x: int, canvas_y: int) -> Tuple[int, int]:
        """Convierte coordenadas del canvas a coordenadas de imagen"""
        if self.current_image is None:
            return canvas_x, canvas_y
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_height, img_width = self.current_image.shape[:2]
        
        # Calcular escalas
        scale_x = img_width / canvas_width if canvas_width > 0 else 1
        scale_y = img_height / canvas_height if canvas_height > 0 else 1
        
        return int(canvas_x * scale_x), int(canvas_y * scale_y)
    
    def start_drawing_rect(self, x: int, y: int):
        """Inicia dibujo de rectángulo"""
        self.rect_start = (x, y)
        self.rect_preview = None
    
    def update_preview_rect(self, x: int, y: int):
        """Actualiza rectángulo de previsualización"""
        if self.rect_start:
            x0, y0 = self.rect_start
            rx, ry = min(x0, x), min(y0, y)
            rw, rh = abs(x - x0), abs(y - y0)
            self.rect_preview = (rx, ry, rw, rh)
    
    def finish_drawing_rect(self):
        """Finaliza dibujo de rectángulo"""
        if self.rect_preview:
            x, y, w, h = self.rect_preview
            if w > 10 and h > 10:  # Tamaño mínimo
                new_space = ParkingSpace(x, y, w, h)
                self.parking_spaces.append(new_space)
                self.set_status(f"Espacio agregado: {len(self.parking_spaces)} total")
                self.update_stats_display()
        
        self.rect_start = None
        self.rect_preview = None
    
    def select_space_at_point(self, x: int, y: int):
        """Selecciona espacio en el punto dado"""
        for i, space in enumerate(self.parking_spaces):
            if space.contains_point(x, y):
                self.selected_space = i
                self.set_status(f"Espacio {i+1} seleccionado")
                return
        
        self.selected_space = None
        self.set_status("Selección limpiada")
    
    # Métodos de archivo
    def save_spaces(self):
        """Guarda espacios en archivo"""
        if not self.parking_spaces:
            messagebox.showwarning("Advertencia", "No hay espacios para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar espacios",
            defaultextension=".pkl",
            filetypes=[("Pickle", "*.pkl"), ("JSON", "*.json"), ("Todos", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    self.save_spaces_json(file_path)
                else:
                    self.save_spaces_pickle(file_path)
                
                self.set_status(f"Espacios guardados: {os.path.basename(file_path)}")
                messagebox.showinfo("Éxito", "Espacios guardados correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron guardar los espacios:\n{e}")
    
    def save_spaces_pickle(self, file_path: str):
        """Guarda espacios en formato pickle (compatibilidad)"""
        spaces_tuples = [space.to_tuple() for space in self.parking_spaces]
        with open(file_path, 'wb') as f:
            pickle.dump(spaces_tuples, f)
    
    def save_spaces_json(self, file_path: str):
        """Guarda espacios en formato JSON"""
        import json
        
        data = {
            'version': '2.0',
            'spaces': [
                {
                    'x': space.x,
                    'y': space.y,
                    'width': space.width,
                    'height': space.height,
                    'id': space.id,
                    'confidence': space.confidence
                }
                for space in self.parking_spaces
            ],
            'metadata': {
                'created': datetime.now().isoformat(),
                'total_spaces': len(self.parking_spaces)
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_spaces(self):
        """Carga espacios desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Cargar espacios",
            filetypes=[("Todos soportados", "*.pkl *.json"), 
                      ("Pickle", "*.pkl"), ("JSON", "*.json"), ("Todos", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    self.load_spaces_json(file_path)
                else:
                    self.load_spaces_pickle(file_path)
                
                count = len(self.parking_spaces)
                self.set_status(f"Espacios cargados: {count} espacios")
                self.update_stats_display()
                messagebox.showinfo("Éxito", f"Se cargaron {count} espacios correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar los espacios:\n{e}")
    
    def load_spaces_pickle(self, file_path: str):
        """Carga espacios desde formato pickle"""
        with open(file_path, 'rb') as f:
            spaces_data = pickle.load(f)
        
        self.parking_spaces = []
        for data in spaces_data:
            if len(data) >= 4:
                x, y, w, h = data[:4]
                space = ParkingSpace(x, y, w, h)
                self.parking_spaces.append(space)
    
    def load_spaces_json(self, file_path: str):
        """Carga espacios desde formato JSON"""
        import json
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.parking_spaces = []
        for space_data in data.get('spaces', []):
            space = ParkingSpace(
                x=space_data['x'],
                y=space_data['y'],
                width=space_data['width'],
                height=space_data['height'],
                id=space_data.get('id'),
                confidence=space_data.get('confidence', 0.0)
            )
            self.parking_spaces.append(space)
    
    def export_results(self):
        """Exporta resultados de análisis"""
        if not self.analysis_history:
            messagebox.showwarning("Advertencia", "No hay resultados de análisis para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar resultados",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json"), ("Todos", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    self.export_results_json(file_path)
                else:
                    self.export_results_csv(file_path)
                
                self.set_status(f"Resultados exportados: {os.path.basename(file_path)}")
                messagebox.showinfo("Éxito", "Resultados exportados correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron exportar los resultados:\n{e}")
    
    def export_results_csv(self, file_path: str):
        """Exporta resultados a CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Total', 'Ocupados', 'Libres', 'Eficiencia_%'])
            
            for record in self.analysis_history:
                writer.writerow([
                    record['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    record['total'],
                    record['occupied'],
                    record['free'],
                    f"{record['efficiency']:.1f}"
                ])
    
    def export_results_json(self, file_path: str):
        """Exporta resultados a JSON"""
        import json
        
        data = {
            'analysis_history': [
                {
                    'timestamp': record['timestamp'].isoformat(),
                    'total': record['total'],
                    'occupied': record['occupied'],
                    'free': record['free'],
                    'efficiency': record['efficiency']
                }
                for record in self.analysis_history
            ],
            'current_state': {
                'total_spaces': len(self.parking_spaces),
                'last_analysis': self.analysis_results
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Métodos auxiliares
    def delete_selected(self):
        """Elimina el espacio seleccionado"""
        if self.selected_space is not None and 0 <= self.selected_space < len(self.parking_spaces):
            del self.parking_spaces[self.selected_space]
            self.selected_space = None
            self.set_status(f"Espacio eliminado. Total: {len(self.parking_spaces)}")
            self.update_stats_display()
    
    def duplicate_selected(self):
        """Duplica el espacio seleccionado"""
        if self.selected_space is not None and 0 <= self.selected_space < len(self.parking_spaces):
            space = self.parking_spaces[self.selected_space]
            new_space = ParkingSpace(
                space.x + 20, space.y + 20, space.width, space.height,
                confidence=space.confidence
            )
            self.parking_spaces.append(new_space)
            self.set_status(f"Espacio duplicado. Total: {len(self.parking_spaces)}")
            self.update_stats_display()
    
    def clear_selection(self):
        """Limpia la selección"""
        self.selected_space = None
        self.set_status("Selección limpiada")
    
    def show_space_properties(self):
        """Muestra propiedades del espacio seleccionado"""
        if self.selected_space is not None and 0 <= self.selected_space < len(self.parking_spaces):
            space = self.parking_spaces[self.selected_space]
            
            props = f"""Propiedades del Espacio {self.selected_space + 1}:

Posición: ({space.x}, {space.y})
Dimensiones: {space.width} x {space.height}
Área: {space.area} píxeles
Centro: {space.center}
Confianza: {space.confidence:.3f}
ID: {space.id or 'Sin asignar'}
"""
            
            if (self.analysis_results and 
                self.selected_space < len(self.analysis_results)):
                status = "Ocupado" if self.analysis_results[self.selected_space] else "Libre"
                props += f"Estado: {status}"
            
            messagebox.showinfo("Propiedades del Espacio", props)
    
    def set_tool(self, tool: str):
        """Establece la herramienta actual"""
        if tool == 'select':
            self.drawing_mode = False
            self.set_status("Herramienta: Seleccionar")
        elif tool == 'draw':
            self.drawing_mode = True
            self.set_status("Herramienta: Dibujar - Arrastra para crear espacio")
    
    def reset_all(self):
        """Reinicia toda la aplicación"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres reiniciar todo?"):
            # Detener video
            self.video_manager.release()
            
            # Limpiar estado
            self.parking_spaces = []
            self.analysis_results = []
            self.analysis_history = []
            self.current_image = None
            self.selected_space = None
            self.is_analyzing = False
            self.analysis_mode = False
            self.drawing_mode = False
            
            # Limpiar canvas
            self.canvas.delete("all")
            
            # Actualizar interfaz
            self.update_stats_display()
            self.set_status("Aplicación reiniciada")

def main():
    """Función principal"""
    root = tk.Tk()
    app = CarParkAppRefactored(root)
    root.mainloop()

if __name__ == "__main__":
    main()
