"""
GUI Simple para CarPark Project
Interfaz funcional con tu analizador simple integrado
"""
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import cv2
import numpy as np
import pickle
from PIL import Image, ImageTk
import os
import sys
from typing import List, Optional

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.simple_analyzer import SimpleOccupancyAnalyzer
    from src.working_analyzer import WorkingOccupancyAnalyzer
    from src.models import ParkingSpace
except ImportError as e:
    print(f"Error importando módulos: {e}")

class CarParkGUI:
    """GUI principal que funciona con tu analizador simple"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🚗 CarPark Project - GUI Principal")
        self.root.geometry("1400x900")
        
        # Variables
        self.current_frame = None
        self.spaces = []
        self.analysis_results = []
        self.video_playing = False
        self.cap = None
        
        # Analizadores
        self.simple_analyzer = SimpleOccupancyAnalyzer(threshold=0.23)
        self.working_analyzer = WorkingOccupancyAnalyzer(pixel_threshold=900)
        self.current_analyzer = "simple"  # Por defecto usar el simple
        
        # Variables de UI
        self.analyzer_var = tk.StringVar(value="simple")
        self.threshold_var = tk.DoubleVar(value=0.23)
        self.pixel_threshold_var = tk.IntVar(value=900)
        
        self.setup_ui()
        self.load_spaces()
    
    def setup_ui(self):
        """Configurar la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - controles
        control_panel = ttk.LabelFrame(main_frame, text="🎛️ Controles Principales", padding=10)
        control_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Fila 1: Selector de analizador
        row1 = ttk.Frame(control_panel)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(row1, text="Analizador:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        analyzer_combo = ttk.Combobox(
            row1, 
            textvariable=self.analyzer_var,
            values=["simple", "working"],
            state="readonly",
            width=12
        )
        analyzer_combo.pack(side=tk.LEFT, padx=(0, 20))
        analyzer_combo.bind('<<ComboboxSelected>>', self.on_analyzer_change)
        
        # Controles de threshold
        ttk.Label(row1, text="Threshold:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.threshold_scale = tk.Scale(
            row1, 
            from_=0.1, to=0.5, 
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            command=self.on_threshold_change,
            length=150
        )
        self.threshold_scale.pack(side=tk.LEFT, padx=(0, 10))
        
        # Controles de archivo
        ttk.Button(row1, text="📁 Cargar Imagen", command=self.load_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="🎥 Cargar Video", command=self.load_video).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="🔍 Analizar", command=self.analyze_current).pack(side=tk.LEFT, padx=(0, 5))
        
        # Panel central - contenido
        content_panel = ttk.Frame(main_frame)
        content_panel.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - imagen/video
        left_panel = ttk.LabelFrame(content_panel, text="📺 Vista Principal", padding=5)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.image_label = ttk.Label(left_panel, text="Carga una imagen o video", anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Panel derecho - resultados y configuración
        right_panel = ttk.Frame(content_panel)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.configure(width=300)
        
        # Resultados
        results_frame = ttk.LabelFrame(right_panel, text="📊 Resultados", padding=10)
        results_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Métricas
        metrics_frame = ttk.Frame(results_frame)
        metrics_frame.pack(fill=tk.X)
        
        # Total
        ttk.Label(metrics_frame, text="Total espacios:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.total_label = ttk.Label(metrics_frame, text="0", font=("Arial", 11, "bold"), foreground="blue")
        self.total_label.grid(row=0, column=1, sticky=tk.E, pady=2)
        
        # Ocupados
        ttk.Label(metrics_frame, text="Ocupados:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.occupied_label = ttk.Label(metrics_frame, text="0", font=("Arial", 11, "bold"), foreground="red")
        self.occupied_label.grid(row=1, column=1, sticky=tk.E, pady=2)
        
        # Libres
        ttk.Label(metrics_frame, text="Libres:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.free_label = ttk.Label(metrics_frame, text="0", font=("Arial", 11, "bold"), foreground="green")
        self.free_label.grid(row=2, column=1, sticky=tk.E, pady=2)
        
        # Porcentaje
        ttk.Label(metrics_frame, text="% Ocupación:", font=("Arial", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.percent_label = ttk.Label(metrics_frame, text="0.0%", font=("Arial", 11, "bold"), foreground="orange")
        self.percent_label.grid(row=3, column=1, sticky=tk.E, pady=2)
        
        # Configurar grid
        metrics_frame.columnconfigure(1, weight=1)
        
        # Configuración del analizador
        config_frame = ttk.LabelFrame(right_panel, text="⚙️ Configuración", padding=10)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Info del analizador actual
        self.info_text = tk.Text(config_frame, height=8, wrap=tk.WORD, font=("Consolas", 8))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Herramientas
        tools_frame = ttk.LabelFrame(right_panel, text="🛠️ Herramientas", padding=10)
        tools_frame.pack(fill=tk.X)
        
        ttk.Button(tools_frame, text="📝 Editor de Espacios", command=self.open_space_editor).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(tools_frame, text="💾 Guardar Configuración", command=self.save_config).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(tools_frame, text="📂 Cargar Configuración", command=self.load_config).pack(fill=tk.X)
        
        # Panel inferior - estado
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="✅ Listo")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Actualizar info inicial
        self.update_analyzer_info()
    
    def on_analyzer_change(self, event=None):
        """Cuando cambia el analizador seleccionado"""
        self.current_analyzer = self.analyzer_var.get()
        self.update_analyzer_info()
        
        # Re-analizar si hay imagen cargada
        if self.current_frame is not None:
            self.analyze_current()
    
    def on_threshold_change(self, value):
        """Cuando cambia el threshold"""
        threshold = float(value)
        
        if self.current_analyzer == "simple":
            self.simple_analyzer.set_threshold(threshold)
        
        # Re-analizar si hay imagen cargada
        if self.current_frame is not None:
            self.analyze_current()
        
        self.update_analyzer_info()
    
    def update_analyzer_info(self):
        """Actualizar información del analizador"""
        self.info_text.delete(1.0, tk.END)
        
        if self.current_analyzer == "simple":
            info = f"""ANALIZADOR SIMPLE
════════════════════

Método: Threshold de intensidad
Threshold: {self.simple_analyzer.get_threshold():.3f}

Funcionamiento:
• Convierte a escala de grises
• Calcula intensidad promedio
• Compara con threshold
• Intensidad < {self.simple_analyzer.get_threshold():.3f} = OCUPADO
• Intensidad ≥ {self.simple_analyzer.get_threshold():.3f} = LIBRE

Ventajas:
• Muy rápido
• Simple de configurar
• Funciona bien con luz estable

Ajustar threshold:
• Más bajo = más sensible
• Más alto = menos sensible"""
        
        else:  # working
            info = f"""ANALIZADOR WORKING
════════════════════

Método: Conteo de píxeles
Threshold: {self.working_analyzer.get_pixel_threshold()} píxeles

Funcionamiento:
• Gaussian blur (3x3)
• Adaptive threshold
• Median filter (5x5)
• Dilatación (3x3)
• Cuenta píxeles blancos
• ≥ {self.working_analyzer.get_pixel_threshold()} píxeles = OCUPADO
• < {self.working_analyzer.get_pixel_threshold()} píxeles = LIBRE

Ventajas:
• Replica código exitoso
• Robusto ante luz
• Preprocesamiento avanzado

Este es el método que
REALMENTE funciona."""
        
        self.info_text.insert(1.0, info)
    
    def load_spaces(self):
        """Cargar espacios desde CarParkPos"""
        try:
            with open('assets/CarParkPos', 'rb') as f:
                pos_list = pickle.load(f)
            
            self.spaces = []
            width, height = 107, 48
            
            for i, (x, y) in enumerate(pos_list):
                space = ParkingSpace(
                    id=f"space_{i}",
                    x=x, y=y,
                    width=width, height=height
                )
                self.spaces.append(space)
            
            self.status_var.set(f"✅ Cargados {len(self.spaces)} espacios")
            self.update_metrics()
            
        except Exception as e:
            self.status_var.set(f"⚠️ Error cargando espacios: {e}")
    
    def load_image(self):
        """Cargar imagen"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")]
        )
        
        if file_path:
            try:
                self.current_frame = cv2.imread(file_path)
                if self.current_frame is None:
                    raise ValueError("No se pudo cargar la imagen")
                
                self.display_frame(self.current_frame)
                self.status_var.set(f"✅ Imagen cargada: {os.path.basename(file_path)}")
                
                # Analizar automáticamente
                if self.spaces:
                    self.analyze_current()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando imagen: {e}")
    
    def load_video(self):
        """Cargar y reproducir video"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar video",
            filetypes=[("Videos", "*.mp4 *.avi *.mov *.mkv"), ("Todos", "*.*")]
        )
        
        if file_path:
            self.play_video(file_path)
    
    def play_video(self, video_path):
        """Reproducir video con análisis"""
        try:
            if self.cap:
                self.cap.release()
            
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                raise ValueError("No se pudo abrir el video")
            
            self.video_playing = True
            self.status_var.set("🎥 Reproduciendo video...")
            self.video_loop()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando video: {e}")
    
    def video_loop(self):
        """Loop de reproducción de video"""
        if not self.video_playing or not self.cap:
            return
        
        ret, frame = self.cap.read()
        
        if not ret:
            # Reiniciar video
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        
        if ret:
            self.current_frame = frame
            
            # Analizar frame
            if self.spaces:
                self.analyze_frame_silent(frame)
            
            # Mostrar frame con análisis
            self.display_frame_with_analysis(frame)
            
            # Programar siguiente frame
            self.root.after(50, self.video_loop)  # 20 FPS
    
    def analyze_current(self):
        """Analizar frame actual"""
        if self.current_frame is None:
            messagebox.showwarning("Advertencia", "No hay imagen cargada")
            return
        
        if not self.spaces:
            messagebox.showwarning("Advertencia", "No hay espacios definidos")
            return
        
        try:
            self.analyze_frame_silent(self.current_frame)
            self.display_frame_with_analysis(self.current_frame)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis: {e}")
    
    def analyze_frame_silent(self, frame):
        """Analizar frame sin mostrar errores"""
        try:
            if self.current_analyzer == "simple":
                self.analysis_results = self.simple_analyzer.analyze_spaces(frame, self.spaces)
            else:
                self.analysis_results = self.working_analyzer.analyze_spaces(frame, self.spaces)
            
            self.update_metrics()
            
        except Exception as e:
            self.status_var.set(f"❌ Error en análisis: {e}")
    
    def update_metrics(self):
        """Actualizar métricas en la interfaz"""
        total = len(self.analysis_results) if self.analysis_results else len(self.spaces)
        occupied = sum(1 for r in self.analysis_results if r.is_occupied) if self.analysis_results else 0
        free = total - occupied
        percent = (occupied / total * 100) if total > 0 else 0
        
        self.total_label.config(text=str(total))
        self.occupied_label.config(text=str(occupied))
        self.free_label.config(text=str(free))
        self.percent_label.config(text=f"{percent:.1f}%")
    
    def display_frame(self, frame):
        """Mostrar frame en la interfaz"""
        try:
            # Redimensionar para ajustar
            height, width = frame.shape[:2]
            max_width, max_height = 800, 600
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convertir para tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Mantener referencia
            
        except Exception as e:
            self.status_var.set(f"❌ Error mostrando imagen: {e}")
    
    def display_frame_with_analysis(self, frame):
        """Mostrar frame con análisis"""
        try:
            display_frame = frame.copy()
            
            # Dibujar espacios
            for i, (space, result) in enumerate(zip(self.spaces, self.analysis_results)):
                color = (0, 0, 255) if result.is_occupied else (0, 255, 0)
                thickness = 3 if result.is_occupied else 2
                
                # Rectángulo
                cv2.rectangle(display_frame, 
                             (space.x, space.y), 
                             (space.x + space.width, space.y + space.height), 
                             color, thickness)
                
                # Número
                cv2.putText(display_frame, str(i), 
                           (space.x + 5, space.y + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Estadísticas en la imagen
            total = len(self.analysis_results)
            occupied = sum(1 for r in self.analysis_results if r.is_occupied)
            free = total - occupied
            
            stats_text = f"Libres: {free}/{total} | {self.current_analyzer.upper()}"
            cv2.putText(display_frame, stats_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            self.display_frame(display_frame)
            
        except Exception as e:
            self.display_frame(frame)
    
    def open_space_editor(self):
        """Abrir editor de espacios simple"""
        try:
            import subprocess
            subprocess.run([sys.executable, "simple_space_editor.py"], 
                          capture_output=False, text=True)
            
            # Recargar espacios después del editor
            self.root.after(1000, self.load_spaces)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo editor: {e}")
    
    def save_config(self):
        """Guardar configuración actual"""
        try:
            config = {
                'analyzer': self.current_analyzer,
                'simple_threshold': self.simple_analyzer.get_threshold(),
                'working_threshold': self.working_analyzer.get_pixel_threshold()
            }
            
            with open('config_analyzer.json', 'w') as f:
                import json
                json.dump(config, f, indent=2)
            
            self.status_var.set("✅ Configuración guardada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {e}")
    
    def load_config(self):
        """Cargar configuración"""
        try:
            with open('config_analyzer.json', 'r') as f:
                import json
                config = json.load(f)
            
            self.analyzer_var.set(config.get('analyzer', 'simple'))
            
            if 'simple_threshold' in config:
                threshold = config['simple_threshold']
                self.threshold_var.set(threshold)
                self.simple_analyzer.set_threshold(threshold)
            
            if 'working_threshold' in config:
                self.working_analyzer.set_pixel_threshold(config['working_threshold'])
            
            self.on_analyzer_change()
            self.status_var.set("✅ Configuración cargada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando configuración: {e}")
    
    def on_closing(self):
        """Al cerrar la aplicación"""
        self.video_playing = False
        if self.cap:
            self.cap.release()
        self.root.destroy()
