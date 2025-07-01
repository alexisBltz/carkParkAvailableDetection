"""
Interfaz de usuario principal del sistema CarPark
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

# Importaciones locales
from .models import ParkingSpace, OccupancyStatus, AnalysisStats
from .video_manager import VideoManager
from .detector import SmartDetector
from .analyzer import OccupancyAnalyzer
from .file_manager import FileManager
from .space_editor import SpaceEditor
import config

class CarParkGUI:
    """Interfaz gráfica principal del sistema CarPark"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_window()
        
        # Componentes del sistema
        self.video_manager = VideoManager()
        self.detector = SmartDetector()
        self.analyzer = OccupancyAnalyzer()
        self.space_editor = None
        
        # Estado de la aplicación
        self.spaces: List[ParkingSpace] = []
        self.current_frame = None
        self.analysis_results: List[OccupancyStatus] = []
        self.stats_history: List[AnalysisStats] = []
        self.is_analyzing = False
        
        # Variables de UI
        self.video_label = None
        self.stats_text = None
        self.analysis_thread = None
        
        self.setup_ui()
        self.setup_bindings()
    
    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title("CarPark Project - Sistema Profesional v3.0")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Video y controles
        self.setup_video_panel(main_frame)
        
        # Panel derecho - Estadísticas y controles
        self.setup_control_panel(main_frame)
        
        # Panel inferior - Barra de estado
        self.setup_status_bar(main_frame)
    
    def setup_video_panel(self, parent):
        """Configura el panel de video"""
        video_frame = ttk.LabelFrame(parent, text="Vista de Video", padding=10)
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Área de video
        self.video_label = tk.Label(video_frame, bg='black', text="Selecciona un video")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Controles de video
        video_controls = ttk.Frame(video_frame)
        video_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(video_controls, text="Cargar Video", 
                  command=self.load_video).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(video_controls, text="Cargar Cámara", 
                  command=self.load_camera).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(video_controls, text="Iniciar/Pausar", 
                  command=self.toggle_analysis).pack(side=tk.LEFT, padx=(0, 5))
        
        # Controles de espacios
        space_controls = ttk.Frame(video_frame)
        space_controls.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(space_controls, text="Detectar Automático", 
                  command=self.detect_spaces).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(space_controls, text="Editor Manual", 
                  command=self.open_space_editor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(space_controls, text="Cargar Espacios", 
                  command=self.load_spaces).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(space_controls, text="Guardar Espacios", 
                  command=self.save_spaces).pack(side=tk.LEFT, padx=(0, 5))
    
    def setup_control_panel(self, parent):
        """Configura el panel de control y estadísticas"""
        control_frame = ttk.LabelFrame(parent, text="Control y Estadísticas", padding=10)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        control_frame.configure(width=350)
        
        # Información del proyecto
        info_frame = ttk.LabelFrame(control_frame, text="Información", padding=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(info_frame, text="CarPark Professional", 
                              font=('Arial', 14, 'bold'), fg='#2E86AB')
        title_label.pack()
        
        version_label = tk.Label(info_frame, text="Versión 3.0 - Modular", 
                               font=('Arial', 10), fg='#666')
        version_label.pack()
        
        # Configuración de análisis
        config_frame = ttk.LabelFrame(control_frame, text="Configuración", padding=5)
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(config_frame, text="Método de Análisis:").pack(anchor=tk.W)
        self.analysis_method = tk.StringVar(value="adaptive")
        method_combo = ttk.Combobox(config_frame, textvariable=self.analysis_method,
                                   values=["fixed", "adaptive", "background"],
                                   state="readonly")
        method_combo.pack(fill=tk.X, pady=(0, 5))
        
        # Estadísticas en tiempo real
        stats_frame = ttk.LabelFrame(control_frame, text="Estadísticas", padding=5)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=15, width=40, 
                                 font=('Courier', 10))
        stats_scroll = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, 
                                    command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de exportación
        export_frame = ttk.LabelFrame(control_frame, text="Exportar", padding=5)
        export_frame.pack(fill=tk.X)
        
        ttk.Button(export_frame, text="Exportar Estadísticas", 
                  command=self.export_stats).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(export_frame, text="Exportar Ocupación", 
                  command=self.export_occupancy).pack(fill=tk.X)
    
    def setup_status_bar(self, parent):
        """Configura la barra de estado"""
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
    
    def setup_bindings(self):
        """Configura eventos y bindings"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # Métodos de control de video
    def load_video(self):
        """Carga un archivo de video"""
        filetypes = [("Videos", "*.mp4 *.avi *.mov *.mkv *.wmv")]
        filepath = filedialog.askopenfilename(
            title="Seleccionar Video",
            filetypes=filetypes,
            initialdir=config.ASSETS_DIR
        )
        
        if filepath:
            if self.video_manager.load_video(filepath):
                self.status_var.set(f"Video cargado: {filepath}")
                self.update_video_display()
            else:
                messagebox.showerror("Error", "No se pudo cargar el video")
    
    def load_camera(self):
        """Carga una cámara"""
        if self.video_manager.load_camera(0):
            self.status_var.set("Cámara cargada")
            self.update_video_display()
        else:
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
    
    def toggle_analysis(self):
        """Inicia o pausa el análisis"""
        if not self.is_analyzing:
            if not self.spaces:
                messagebox.showwarning("Advertencia", 
                                     "Define espacios primero")
                return
            
            self.is_analyzing = True
            self.video_manager.start_capture(self.on_frame_received)
            self.status_var.set("Análisis iniciado")
        else:
            self.is_analyzing = False
            self.video_manager.pause_capture()
            self.status_var.set("Análisis pausado")
    
    def on_frame_received(self, frame):
        """Callback cuando se recibe un nuevo frame"""
        if not self.is_analyzing or not self.spaces:
            return
        
        self.current_frame = frame.copy()
        
        # Realizar análisis
        method = self.analysis_method.get()
        self.analysis_results = self.analyzer.analyze_with_history(
            frame, self.spaces, method
        )
        
        # Actualizar estadísticas
        stats = self.analyzer.calculate_statistics(self.analysis_results)
        self.stats_history.append(stats)
        
        # Actualizar UI (debe ser thread-safe)
        self.root.after(0, self.update_ui_from_analysis)
    
    def update_ui_from_analysis(self):
        """Actualiza la UI con los resultados del análisis"""
        self.update_video_display()
        self.update_statistics_display()
    
    def update_video_display(self):
        """Actualiza la visualización del video"""
        frame = self.current_frame
        if frame is None:
            frame = self.video_manager.get_frame()
        
        if frame is not None:
            # Dibujar espacios
            display_frame = self.draw_spaces_on_frame(frame.copy())
            
            # Convertir para Tkinter
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            h, w = display_frame.shape[:2]
            
            # Escalar para ajustar al widget
            widget_w = self.video_label.winfo_width()
            widget_h = self.video_label.winfo_height()
            
            if widget_w > 1 and widget_h > 1:
                scale = min(widget_w / w, widget_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
                display_frame = cv2.resize(display_frame, (new_w, new_h))
            
            # Mostrar en widget
            image = Image.fromarray(display_frame)
            photo = ImageTk.PhotoImage(image)
            self.video_label.configure(image=photo, text="")
            self.video_label.image = photo
    
    def draw_spaces_on_frame(self, frame):
        """Dibuja los espacios en el frame"""
        for i, space in enumerate(self.spaces):
            # Determinar color basado en ocupación
            color = (0, 255, 0)  # Verde por defecto
            
            if self.analysis_results and i < len(self.analysis_results):
                result = self.analysis_results[i]
                if result.is_occupied:
                    color = (0, 0, 255)  # Rojo ocupado
                else:
                    color = (0, 255, 0)  # Verde libre
            
            # Dibujar rectángulo
            cv2.rectangle(frame, (space.x, space.y), 
                         (space.x + space.width, space.y + space.height), 
                         color, 2)
            
            # Dibujar ID
            if space.id:
                cv2.putText(frame, space.id, (space.x, space.y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return frame
    
    def update_statistics_display(self):
        """Actualiza la visualización de estadísticas"""
        if not self.stats_history:
            return
        
        stats = self.stats_history[-1]
        
        text = f"""=== ESTADÍSTICAS ACTUALES ===
Timestamp: {datetime.now().strftime('%H:%M:%S')}

Total de Espacios: {stats.total_spaces}
Espacios Ocupados: {stats.occupied_spaces}
Espacios Libres: {stats.free_spaces}

Tasa de Ocupación: {stats.occupancy_rate:.1f}%
Tasa de Disponibilidad: {stats.availability_rate:.1f}%

=== DETALLES POR ESPACIO ===
"""
        
        for result in self.analysis_results:
            status = "OCUPADO" if result.is_occupied else "LIBRE"
            text += f"{result.space_id}: {status} ({result.confidence:.2f})\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, text)
    
    # Métodos de gestión de espacios
    def detect_spaces(self):
        """Detecta espacios automáticamente"""
        if self.current_frame is None:
            frame = self.video_manager.get_frame()
        else:
            frame = self.current_frame
        
        if frame is not None:
            self.spaces = self.detector.detect_spaces_combined(frame)
            self.status_var.set(f"Detectados {len(self.spaces)} espacios")
            self.update_video_display()
        else:
            messagebox.showwarning("Advertencia", "Carga un video primero")
    
    def open_space_editor(self):
        """Abre el editor de espacios"""
        if self.current_frame is None:
            frame = self.video_manager.get_frame()
        else:
            frame = self.current_frame
        
        if frame is not None:
            self.space_editor = SpaceEditor(self.root, frame, self.spaces)
            self.space_editor.show(self.on_spaces_edited)
        else:
            messagebox.showwarning("Advertencia", "Carga un video primero")
    
    def on_spaces_edited(self, edited_spaces):
        """Callback cuando se editan espacios"""
        self.spaces = edited_spaces
        self.status_var.set(f"Espacios editados: {len(self.spaces)}")
        self.update_video_display()
    
    def load_spaces(self):
        """Carga espacios desde archivo"""
        filetypes = [
            ("Archivos JSON", "*.json"),
            ("Archivos Pickle", "*.pkl *.pickle"),
            ("Todos", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Cargar Espacios",
            filetypes=filetypes,
            initialdir=config.ASSETS_DIR
        )
        
        if filepath:
            spaces = FileManager.auto_load_spaces(filepath)
            if spaces:
                self.spaces = spaces
                self.status_var.set(f"Cargados {len(spaces)} espacios")
                self.update_video_display()
            else:
                messagebox.showerror("Error", "No se pudieron cargar los espacios")
    
    def save_spaces(self):
        """Guarda espacios en archivo"""
        if not self.spaces:
            messagebox.showwarning("Advertencia", "No hay espacios para guardar")
            return
        
        filetypes = [("Archivos JSON", "*.json")]
        filepath = filedialog.asksaveasfilename(
            title="Guardar Espacios",
            filetypes=filetypes,
            defaultextension=".json",
            initialdir=config.ASSETS_DIR
        )
        
        if filepath:
            if FileManager.save_spaces_json(self.spaces, filepath):
                self.status_var.set("Espacios guardados")
            else:
                messagebox.showerror("Error", "No se pudieron guardar los espacios")
    
    # Métodos de exportación
    def export_stats(self):
        """Exporta estadísticas a CSV"""
        if not self.stats_history:
            messagebox.showwarning("Advertencia", "No hay estadísticas para exportar")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Exportar Estadísticas",
            filetypes=[("CSV", "*.csv")],
            defaultextension=".csv"
        )
        
        if filepath:
            if FileManager.export_analysis_csv(self.stats_history, filepath):
                messagebox.showinfo("Éxito", "Estadísticas exportadas")
            else:
                messagebox.showerror("Error", "Error al exportar")
    
    def export_occupancy(self):
        """Exporta historial de ocupación a CSV"""
        messagebox.showinfo("Info", "Función de exportación de ocupación pendiente")
    
    def on_closing(self):
        """Limpia recursos al cerrar"""
        self.is_analyzing = False
        self.video_manager.stop_capture()
        self.video_manager.release()
        self.root.destroy()


def main():
    """Función principal"""
    root = tk.Tk()
    app = CarParkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
