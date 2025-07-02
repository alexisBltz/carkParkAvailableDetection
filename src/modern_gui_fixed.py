"""
GUI Moderna Completa para CarPark Project v3.0
Interfaz completamente funcional con todas las características
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading
import time
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

# Importaciones locales
from .models import ParkingSpace, OccupancyStatus, AnalysisStats
from .video_manager import VideoManager
from .detector import SmartDetector
from .analyzer import OccupancyAnalyzer
from .file_manager import FileManager
from .space_editor import SpaceEditor
from .legacy_detector import LegacyOccupancyDetector
from .modern_theme import ModernDarkTheme, ModernWidgets, ModernTooltip

# Importar config
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import config

class ModernCarParkGUI:
    """Interfaz gráfica moderna del sistema CarPark"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.setup_modern_window()
        
        # Componentes del sistema
        self.video_manager = VideoManager()
        self.detector = SmartDetector()
        self.analyzer = OccupancyAnalyzer()
        self.legacy_detector = LegacyOccupancyDetector()
        
        # Estado de la aplicación
        self.spaces: List[ParkingSpace] = []
        self.current_frame = None
        self.analysis_results: List[OccupancyStatus] = []
        self.is_analyzing = False
        
        # Variables de UI modernas
        self.main_notebook = None
        self.video_canvas = None
        self.editor_canvas = None
        self.status_labels = {}
        self.progress_vars = {}
        self.status_var = tk.StringVar(value="🚀 CarPark Professional iniciado")
        self.analysis_method = tk.StringVar(value="adaptive")
        
        # Variables para edición
        self.drawing_mode = False
        self.selection_mode = False
        self.drawing_start = None
        self.temp_rectangle = None
        self.selected_space = None
        self.clipboard_spaces = []
        self.undo_stack = []
        
        self.setup_modern_ui()
        self.setup_bindings()
    
    def setup_modern_window(self):
        """Configura la ventana principal con estilo moderno"""
        self.root.title("🚗 CarPark Professional v3.0")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 800)
        
        # Configurar tema oscuro
        self.style = ModernDarkTheme.configure_styles(self.root)
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_modern_ui(self):
        """Configura la interfaz de usuario moderna"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Crear barra de título moderna
        self.create_title_section(main_frame)
        
        # Crear notebook principal con pestañas
        self.create_main_notebook(main_frame)
        
        # Crear barra de estado moderna
        self.create_modern_status_bar(main_frame)
    
    def create_title_section(self, parent):
        """Crea la sección de título moderna"""
        title_frame = ModernWidgets.create_title_bar(
            parent,
            "🚗 CarPark Professional",
            "Sistema avanzado de detección de espacios de estacionamiento v3.0"
        )
    
    def create_main_notebook(self, parent):
        """Crea el notebook principal con pestañas modernas"""
        self.main_notebook = ttk.Notebook(parent)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Pestaña 1: Monitor Principal
        self.create_monitor_tab()
        
        # Pestaña 2: Editor de Espacios
        self.create_editor_tab()
        
        # Configurar binding para cambio de pestaña
        self.main_notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_monitor_tab(self):
        """Crea la pestaña de monitoreo principal"""
        monitor_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(monitor_frame, text="📺 Monitor Principal")
        
        # Panel izquierdo - Video
        left_panel = ttk.Frame(monitor_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video card
        video_card = ModernWidgets.create_info_card(
            left_panel, "Vista en Tiempo Real", "", "🎥"
        )
        video_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas para video con borde moderno
        canvas_frame = ttk.Frame(video_card)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.video_canvas = tk.Canvas(
            canvas_frame,
            bg=ModernDarkTheme.COLORS['bg_secondary'],
            highlightthickness=2,
            highlightcolor=ModernDarkTheme.COLORS['accent_blue'],
            highlightbackground=ModernDarkTheme.COLORS['border_medium']
        )
        self.video_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controles de video modernos
        self.create_video_controls(left_panel)
        
        # Panel derecho - Información
        right_panel = ttk.Frame(monitor_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.configure(width=350)
        
        self.create_info_panel(right_panel)
    
    def create_video_controls(self, parent):
        """Crea controles de video modernos"""
        controls_card = ModernWidgets.create_info_card(
            parent, "Controles de Video", "", "🎮"
        )
        controls_card.pack(fill=tk.X)
        
        # Frame para botones
        buttons_frame = ttk.Frame(controls_card)
        buttons_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Primera fila de botones
        row1 = ttk.Frame(buttons_frame)
        row1.pack(fill=tk.X, pady=(0, 10))
        
        load_video_btn = ModernWidgets.create_action_button(
            row1, "Cargar Video", self.load_video, "Action.TButton", "📁"
        )
        load_video_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_camera_btn = ModernWidgets.create_action_button(
            row1, "Cámara Web", self.load_camera, "Action.TButton", "📹"
        )
        load_camera_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Segunda fila de botones
        row2 = ttk.Frame(buttons_frame)
        row2.pack(fill=tk.X, pady=(0, 10))
        
        play_btn = ModernWidgets.create_action_button(
            row2, "Reproducir", self.toggle_video, "Success.TButton", "▶️"
        )
        play_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        snapshot_btn = ModernWidgets.create_action_button(
            row2, "Captura", self.take_snapshot, "Action.TButton", "📸"
        )
        snapshot_btn.pack(side=tk.LEFT)
    
    def create_info_panel(self, parent):
        """Crea el panel de información lateral"""
        # Estadísticas en tiempo real
        stats_card = ModernWidgets.create_info_card(
            parent, "Estadísticas en Tiempo Real", "", "📊"
        )
        stats_card.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para estadísticas
        stats_frame = ttk.Frame(stats_card)
        stats_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Crear etiquetas de estadísticas
        self.create_stats_labels(stats_frame)
        
        # Configuración rápida
        config_card = ModernWidgets.create_info_card(
            parent, "Configuración Rápida", "", "⚙️"
        )
        config_card.pack(fill=tk.X, pady=(0, 10))
        
        config_frame = ttk.Frame(config_card)
        config_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Selector de método de análisis
        ttk.Label(config_frame, text="Método de Análisis:").pack(anchor=tk.W, pady=(0, 5))
        method_combo = ttk.Combobox(
            config_frame, 
            textvariable=self.analysis_method,
            values=["adaptive", "background", "fixed", "smart"],
            state="readonly"
        )
        method_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Controles de espacios
        spaces_card = ModernWidgets.create_info_card(
            parent, "Gestión de Espacios", "", "🚗"
        )
        spaces_card.pack(fill=tk.BOTH, expand=True)
        
        spaces_frame = ttk.Frame(spaces_card)
        spaces_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.create_spaces_controls(spaces_frame)
    
    def create_stats_labels(self, parent):
        """Crea las etiquetas de estadísticas"""
        # Espacios totales
        total_frame = ttk.Frame(parent)
        total_frame.pack(fill=tk.X, pady=2)
        ttk.Label(total_frame, text="Espacios Totales:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        self.status_labels['total_spaces'] = ttk.Label(total_frame, text="0", foreground=ModernDarkTheme.COLORS['accent_blue'])
        self.status_labels['total_spaces'].pack(side=tk.RIGHT)
        
        # Espacios libres
        free_frame = ttk.Frame(parent)
        free_frame.pack(fill=tk.X, pady=2)
        ttk.Label(free_frame, text="Espacios Libres:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        self.status_labels['free_spaces'] = ttk.Label(free_frame, text="0", foreground=ModernDarkTheme.COLORS['accent_green'])
        self.status_labels['free_spaces'].pack(side=tk.RIGHT)
        
        # Espacios ocupados
        occupied_frame = ttk.Frame(parent)
        occupied_frame.pack(fill=tk.X, pady=2)
        ttk.Label(occupied_frame, text="Espacios Ocupados:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        self.status_labels['occupied_spaces'] = ttk.Label(occupied_frame, text="0", foreground=ModernDarkTheme.COLORS['accent_red'])
        self.status_labels['occupied_spaces'].pack(side=tk.RIGHT)
        
        # Porcentaje de ocupación
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        percent_frame = ttk.Frame(parent)
        percent_frame.pack(fill=tk.X, pady=2)
        ttk.Label(percent_frame, text="Ocupación:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        self.status_labels['occupancy_percent'] = ttk.Label(percent_frame, text="0%", foreground=ModernDarkTheme.COLORS['accent_orange'])
        self.status_labels['occupancy_percent'].pack(side=tk.RIGHT)
        
        # Barra de progreso de ocupación
        self.progress_vars['occupancy'] = tk.DoubleVar()
        occupancy_progress = ttk.Progressbar(
            parent, 
            variable=self.progress_vars['occupancy'],
            maximum=100
        )
        occupancy_progress.pack(fill=tk.X, pady=(5, 10))
    
    def create_spaces_controls(self, parent):
        """Crea controles para gestión de espacios"""
        # Botones de espacios
        detect_btn = ModernWidgets.create_action_button(
            parent, "🔍 Detectar Auto", self.detect_spaces, "Action.TButton", ""
        )
        detect_btn.pack(fill=tk.X, pady=(0, 5))
        
        edit_btn = ModernWidgets.create_action_button(
            parent, "✏️ Editor Moderno", self.open_space_editor, "Action.TButton", ""
        )
        edit_btn.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        load_btn = ModernWidgets.create_action_button(
            parent, "📂 Cargar Espacios", self.load_spaces, "TButton", ""
        )
        load_btn.pack(fill=tk.X, pady=(0, 5))
        
        save_btn = ModernWidgets.create_action_button(
            parent, "💾 Guardar Espacios", self.save_spaces, "Success.TButton", ""
        )
        save_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Separador para análisis
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Controles de análisis en tiempo real
        analysis_label = ttk.Label(parent, text="Análisis en Tiempo Real", font=('Segoe UI', 10, 'bold'))
        analysis_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Botón de iniciar/pausar análisis
        self.analysis_btn = ModernWidgets.create_action_button(
            parent, "▶️ Iniciar Análisis", self.toggle_analysis, "Action.TButton", ""
        )
        self.analysis_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Estado del análisis
        self.analysis_status_label = ttk.Label(
            parent, 
            text="❌ Análisis detenido", 
            foreground=ModernDarkTheme.COLORS['text_secondary']
        )
        self.analysis_status_label.pack(anchor=tk.W, pady=(0, 5))
    
    def create_editor_tab(self):
        """Crea la pestaña del editor de espacios"""
        editor_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(editor_frame, text="✏️ Editor de Espacios")
        
        # Panel superior - Herramientas
        tools_card = ModernWidgets.create_info_card(
            editor_frame, "Herramientas de Edición", "", "🛠️"
        )
        tools_card.pack(fill=tk.X, padx=10, pady=10)
        
        tools_frame = ttk.Frame(tools_card)
        tools_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Primera fila de botones
        tools_row1 = ttk.Frame(tools_frame)
        tools_row1.pack(fill=tk.X, pady=(0, 5))
        
        load_img_btn = ModernWidgets.create_action_button(
            tools_row1, "🖼️ Cargar Imagen", self.load_image_for_editor, "TButton", ""
        )
        load_img_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        detect_auto_btn = ModernWidgets.create_action_button(
            tools_row1, "🔍 Detectar Auto", self.detect_spaces, "Action.TButton", ""
        )
        detect_auto_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_spaces_btn = ModernWidgets.create_action_button(
            tools_row1, "📂 Cargar Espacios", self.load_spaces, "TButton", ""
        )
        load_spaces_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_spaces_btn = ModernWidgets.create_action_button(
            tools_row1, "💾 Guardar Espacios", self.save_spaces, "Success.TButton", ""
        )
        save_spaces_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Segunda fila de botones
        tools_row2 = ttk.Frame(tools_frame)
        tools_row2.pack(fill=tk.X)
        
        draw_btn = ModernWidgets.create_action_button(
            tools_row2, "✏️ Dibujar Espacios", self.start_drawing_mode, "Action.TButton", ""
        )
        draw_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        select_btn = ModernWidgets.create_action_button(
            tools_row2, "👆 Seleccionar", self.start_selection_mode, "TButton", ""
        )
        select_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ModernWidgets.create_action_button(
            tools_row2, "🗑️ Limpiar Todo", self.clear_all_spaces, "Warning.TButton", ""
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Panel central - Canvas de edición
        canvas_card = ModernWidgets.create_info_card(
            editor_frame, "Canvas de Edición", "", "🎨"
        )
        canvas_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        canvas_container = ttk.Frame(canvas_card)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Canvas para edición con scrollbars
        self.editor_canvas = tk.Canvas(
            canvas_container,
            bg=ModernDarkTheme.COLORS['bg_secondary'],
            highlightthickness=2,
            highlightcolor=ModernDarkTheme.COLORS['accent_blue'],
            highlightbackground=ModernDarkTheme.COLORS['border_medium'],
            cursor="crosshair"
        )
        
        # Scrollbars para el canvas
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.editor_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.editor_canvas.xview)
        self.editor_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars y canvas
        self.editor_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bindings para dibujo
        self.editor_canvas.bind("<Button-1>", self.on_canvas_click)
        self.editor_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.editor_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Panel inferior - Información de espacios
        info_card = ModernWidgets.create_info_card(
            editor_frame, "Información de Espacios", "", "📊"
        )
        info_card.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        info_frame = ttk.Frame(info_card)
        info_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.editor_info_label = ttk.Label(
            info_frame, 
            text="Espacios definidos: 0 | Modo: Visualización",
            font=('Segoe UI', 9)
        )
        self.editor_info_label.pack(anchor=tk.W)
    
    def create_modern_status_bar(self, parent):
        """Crea la barra de estado moderna"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status con icono
        ttk.Label(status_frame, text="📍 Estado:", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Hora en el lado derecho
        self.time_label = ttk.Label(status_frame, text="", font=('Segoe UI', 9))
        self.time_label.pack(side=tk.RIGHT)
        
        # Actualizar tiempo cada segundo
        self.update_time()
    
    def update_time(self):
        """Actualiza la hora en la barra de estado"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=f"🕒 {current_time}")
        self.root.after(1000, self.update_time)
    
    def setup_bindings(self):
        """Configura eventos y bindings"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Atajos de teclado para el editor
        self.root.bind('<Control-c>', self.copy_selected_space)
        self.root.bind('<Control-v>', self.paste_spaces)
        self.root.bind('<Control-z>', self.undo_action)
        self.root.bind('<Delete>', self.delete_selected_space)
        self.root.bind('<Escape>', self.exit_all_modes)
        
        # Focus para que los atajos funcionen
        self.root.focus_set()
    
    def on_tab_changed(self, event):
        """Maneja el cambio de pestaña para actualizar visualización"""
        try:
            current_tab = self.main_notebook.select()
            tab_text = self.main_notebook.tab(current_tab, "text")
            
            if "Editor de Espacios" in tab_text:
                self.root.after(100, self.refresh_editor_display)
                
        except Exception as e:
            print(f"Error en cambio de pestaña: {e}")
    
    def refresh_editor_display(self):
        """Refresca la visualización del editor"""
        if self.current_frame is not None:
            try:
                self.display_image_in_editor()
                self.root.update_idletasks()
            except Exception as e:
                print(f"Error refrescando display del editor: {e}")
    
    # Métodos de funcionalidad principal
    def load_video(self):
        """Carga un archivo de video"""
        filetypes = [("Videos", "*.mp4 *.avi *.mov *.mkv *.wmv")]
        filepath = filedialog.askopenfilename(
            title="Seleccionar Video",
            filetypes=filetypes,
            initialdir=getattr(config, 'ASSETS_DIR', 'assets')
        )
        
        if filepath:
            if self.video_manager.load_video(filepath):
                frame = self.video_manager.get_frame()
                if frame is not None:
                    self.current_frame = frame
                    self.update_video_display()
                    self.refresh_editor_display()
                    
                self.status_var.set(f"✅ Video cargado: {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", "No se pudo cargar el video")
    
    def load_camera(self):
        """Conecta una cámara web"""
        if self.video_manager.load_camera():
            frame = self.video_manager.get_frame()
            if frame is not None:
                self.current_frame = frame
                self.update_video_display()
                self.refresh_editor_display()
            
            self.status_var.set("📹 Cámara web conectada")
        else:
            messagebox.showerror("Error", "No se pudo conectar la cámara")
    
    def toggle_video(self):
        """Controla la reproducción del video"""
        if hasattr(self.video_manager, 'is_paused'):
            self.video_manager.is_paused = not self.video_manager.is_paused
            status = "pausado" if self.video_manager.is_paused else "reproduciendo"
            self.status_var.set(f"🎥 Video {status}")
    
    def toggle_analysis(self):
        """Inicia/pausa el análisis en tiempo real"""
        if not self.is_analyzing:
            # Verificar que hay espacios definidos
            if not self.spaces:
                messagebox.showwarning(
                    "Sin espacios", 
                    "Primero debes definir espacios de estacionamiento.\n\n" +
                    "Opciones:\n" +
                    "• Usar '🔍 Detectar Auto' para detección automática\n" +
                    "• Usar '✏️ Editor Moderno' para dibujar manualmente\n" +
                    "• Usar '📂 Cargar Espacios' para cargar desde archivo"
                )
                return
            
            # Verificar que hay video/cámara
            if self.current_frame is None:
                messagebox.showwarning(
                    "Sin video", 
                    "Primero debes cargar un video o conectar una cámara.\n\n" +
                    "Ve a los controles de video y:\n" +
                    "• Carga un video\n" +
                    "• Conecta una cámara web"
                )
                return
            
            # Iniciar análisis
            self.is_analyzing = True
            self.status_var.set("🔄 Análisis en tiempo real iniciado...")
            
            # Actualizar botón
            self.analysis_btn.configure(text="⏸️ Pausar Análisis")
            self.analysis_status_label.configure(
                text="✅ Análisis activo", 
                foreground=ModernDarkTheme.COLORS['accent_green']
            )
            
            # Iniciar hilo de análisis
            threading.Thread(target=self.analysis_loop, daemon=True).start()
            
        else:
            # Detener análisis
            self.is_analyzing = False
            self.status_var.set("⏸️ Análisis pausado")
            
            # Actualizar botón
            self.analysis_btn.configure(text="▶️ Iniciar Análisis")
            self.analysis_status_label.configure(
                text="⏸️ Análisis pausado", 
                foreground=ModernDarkTheme.COLORS['accent_orange']
            )
    
    def analysis_loop(self):
        """Bucle principal de análisis en tiempo real"""
        while self.is_analyzing:
            try:
                # Obtener frame actual
                frame = self.video_manager.get_frame() if self.video_manager.cap else self.current_frame
                
                if frame is not None:
                    self.current_frame = frame
                    
                    # Analizar espacios si están definidos
                    if self.spaces:
                        method = self.analysis_method.get()
                        
                        if method == "adaptive":
                            self.analysis_results = self.analyzer.analyze_adaptive_threshold(frame, self.spaces)
                        elif method == "background":
                            self.analysis_results = self.analyzer.analyze_background_subtraction(frame, self.spaces)
                        elif method == "fixed":
                            self.analysis_results = self.analyzer.analyze_fixed_threshold(frame, self.spaces)
                        elif method == "smart":
                            self.analysis_results = self.analyzer.analyze_with_history(frame, self.spaces, "adaptive")
                        
                        # Actualizar estadísticas en tiempo real
                        self.root.after(0, self.update_real_time_stats)
                    
                    # Actualizar display
                    self.root.after(0, self.update_video_display)
                
                # Controlar velocidad de análisis
                time.sleep(0.5)  # Análisis cada 500ms
                
            except Exception as e:
                print(f"Error en analysis_loop: {e}")
                time.sleep(1)
    
    def update_real_time_stats(self):
        """Actualiza las estadísticas en tiempo real"""
        if self.analysis_results:
            total_spaces = len(self.analysis_results)
            
            # Contar ocupados
            if hasattr(self.analysis_results[0], 'is_occupied'):
                occupied_count = sum(1 for result in self.analysis_results if result.is_occupied)
            else:
                occupied_count = sum(1 for result in self.analysis_results if result)
            
            free_count = total_spaces - occupied_count
            occupancy_percent = (occupied_count / total_spaces * 100) if total_spaces > 0 else 0
            
            # Actualizar labels
            self.status_labels['total_spaces'].configure(text=str(total_spaces))
            self.status_labels['free_spaces'].configure(text=str(free_count))
            self.status_labels['occupied_spaces'].configure(text=str(occupied_count))
            self.status_labels['occupancy_percent'].configure(text=f"{occupancy_percent:.1f}%")
            
            # Actualizar barra de progreso
            self.progress_vars['occupancy'].set(occupancy_percent)
    
    def update_video_display(self):
        """Actualiza la visualización del video"""
        if self.current_frame is None or self.video_canvas is None:
            return
        
        try:
            # Obtener dimensiones del canvas
            self.video_canvas.update_idletasks()
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 800
                canvas_height = 600
            
            # Dibujar espacios en el frame
            display_frame = self.current_frame.copy()
            if self.spaces:
                self.draw_spaces_on_frame(display_frame)
            
            # Redimensionar frame para ajustar al canvas
            height, width = display_frame.shape[:2]
            scale = min(canvas_width / width, canvas_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            if new_width > 0 and new_height > 0:
                frame_resized = cv2.resize(display_frame, (new_width, new_height))
                
                # Convertir a RGB
                if len(frame_resized.shape) == 3:
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                else:
                    frame_rgb = frame_resized
                
                # Crear imagen Tkinter
                image = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image)
                
                # Centrar imagen en canvas
                self.video_canvas.delete("all")
                x_center = canvas_width // 2
                y_center = canvas_height // 2
                
                self.video_canvas.create_image(x_center, y_center, image=photo, anchor="center")
                
                # Mantener referencia
                self.current_video_photo = photo
            
        except Exception as e:
            print(f"Error actualizando video: {e}")
            self.video_canvas.delete("all")
            self.video_canvas.create_text(
                self.video_canvas.winfo_width()//2, 
                self.video_canvas.winfo_height()//2,
                text="Error al mostrar video",
                fill="white",
                font=("Arial", 16)
            )
    
    def draw_spaces_on_frame(self, frame):
        """Dibuja los espacios en el frame"""
        for i, space in enumerate(self.spaces):
            # Determinar color según estado
            if i < len(self.analysis_results):
                if hasattr(self.analysis_results[i], 'is_occupied'):
                    status = self.analysis_results[i]
                    color = (0, 255, 0) if not status.is_occupied else (0, 0, 255)
                else:
                    # Resultado legacy (boolean)
                    is_occupied = self.analysis_results[i]
                    color = (0, 255, 0) if not is_occupied else (0, 0, 255)
                thickness = 3
            else:
                color = (255, 255, 0)  # Amarillo para espacios sin analizar
                thickness = 2
            
            # Dibujar rectángulo
            cv2.rectangle(frame, (space.x, space.y), 
                         (space.x + space.width, space.y + space.height), 
                         color, thickness)
            
            # Dibujar número del espacio
            cv2.putText(frame, str(i + 1), 
                       (space.x + 5, space.y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def take_snapshot(self):
        """Toma una captura de pantalla"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)
            self.status_var.set(f"📸 Captura guardada: {filename}")
        else:
            messagebox.showwarning("Advertencia", "No hay video cargado")
    
    def detect_spaces(self):
        """Detecta espacios automáticamente"""
        if self.current_frame is not None:
            # Usar el detector combinado para mejores resultados
            spaces = self.detector.detect_spaces_combined(self.current_frame)
            if spaces:
                self.spaces = spaces
                self.status_var.set(f"🔍 Detectados {len(spaces)} espacios automáticamente")
                
                # Actualizar visualización
                self.update_video_display()
                self.refresh_editor_display()
                
                # Actualizar contador de espacios
                if hasattr(self, 'editor_info_label'):
                    self.editor_info_label.configure(
                        text=f"Espacios definidos: {len(self.spaces)} | Modo: Visualización"
                    )
            else:
                messagebox.showinfo("Detección", "No se detectaron espacios automáticamente.\nPrueba ajustar la imagen o usar el editor manual.")
        else:
            messagebox.showwarning("Advertencia", "Carga un video o imagen primero")
    
    def open_space_editor(self):
        """Abre el editor de espacios moderno"""
        if self.current_frame is not None:
            self.space_editor = SpaceEditor(self.root, self.current_frame, self.spaces)
            self.space_editor.show(self.on_spaces_updated)
        else:
            messagebox.showwarning("Advertencia", "Carga un video o imagen primero")
    
    def on_spaces_updated(self, spaces: List[ParkingSpace]):
        """Callback cuando se actualizan los espacios"""
        self.spaces = spaces
        self.status_var.set(f"✅ Espacios actualizados: {len(spaces)}")
        
        # Actualizar visualización
        self.update_video_display()
        self.refresh_editor_display()
        
        # Actualizar contador
        if hasattr(self, 'editor_info_label'):
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: Visualización"
            )
    
    def load_spaces(self):
        """Carga espacios desde archivo"""
        filetypes = [
            ("Archivos JSON", "*.json"),
            ("Archivo Legacy CarParkPos", "CarParkPos"),
            ("Archivos Legacy (Sin extensión)", "*"),
            ("Todos los archivos", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Cargar Espacios",
            filetypes=filetypes,
            initialdir=getattr(config, 'ASSETS_DIR', 'assets')
        )
        
        if filepath:
            try:
                # Intentar cargar como JSON primero
                if filepath.endswith('.json'):
                    spaces = FileManager.load_spaces_json(filepath)
                    if spaces:
                        self.spaces = spaces
                        self.status_var.set(f"📂 Cargados {len(spaces)} espacios desde JSON")
                    else:
                        messagebox.showerror("Error", "No se pudieron cargar los espacios JSON")
                        return
                else:
                    # Intentar cargar como archivo legacy (pickle)
                    import pickle
                    with open(filepath, 'rb') as f:
                        positions = pickle.load(f)
                    
                    # Convertir posiciones legacy a espacios modernos
                    spaces = []
                    default_width = 107
                    default_height = 48
                    
                    for i, pos in enumerate(positions):
                        if len(pos) >= 2:
                            if len(pos) == 2:
                                x, y = pos
                                w, h = default_width, default_height
                            else:
                                x, y = pos[0], pos[1]
                                w = pos[2] if len(pos) > 2 else default_width
                                h = pos[3] if len(pos) > 3 else default_height
                            
                            space = ParkingSpace(
                                id=str(i),
                                x=int(x),
                                y=int(y),
                                width=int(w),
                                height=int(h)
                            )
                            spaces.append(space)
                    
                    if spaces:
                        self.spaces = spaces
                        self.status_var.set(f"📂 Cargados {len(spaces)} espacios desde archivo legacy")
                    else:
                        messagebox.showwarning("Advertencia", "No se encontraron espacios en el archivo")
                        return
                
                # Actualizar visualización
                self.update_video_display()
                self.refresh_editor_display()
                
                # Actualizar contador
                if hasattr(self, 'editor_info_label'):
                    self.editor_info_label.configure(
                        text=f"Espacios definidos: {len(self.spaces)} | Modo: Visualización"
                    )
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando espacios: {e}")
    
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
            initialdir=getattr(config, 'ASSETS_DIR', 'assets')
        )
        
        if filepath:
            if FileManager.save_spaces_json(self.spaces, filepath):
                self.status_var.set("💾 Espacios guardados correctamente")
            else:
                messagebox.showerror("Error", "No se pudieron guardar los espacios")
    
    # Métodos del editor
    def display_image_in_editor(self):
        """Muestra la imagen actual en el canvas del editor"""
        if self.current_frame is not None and hasattr(self, 'editor_canvas') and self.editor_canvas is not None:
            try:
                # Obtener dimensiones
                height, width = self.current_frame.shape[:2]
                
                self.editor_canvas.update_idletasks()
                canvas_width = self.editor_canvas.winfo_width()
                canvas_height = self.editor_canvas.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width = 800
                    canvas_height = 600
                
                # Calcular escala
                scale_w = canvas_width / width
                scale_h = canvas_height / height
                scale = min(scale_w, scale_h, 1.0)
                
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                if new_width > 0 and new_height > 0:
                    resized_frame = cv2.resize(self.current_frame, (new_width, new_height))
                    
                    # Convertir a formato Tkinter
                    image_pil = Image.fromarray(resized_frame)
                    photo = ImageTk.PhotoImage(image_pil)
                    
                    # Mostrar en canvas
                    self.editor_canvas.delete("image")
                    self.editor_canvas.create_image(
                        canvas_width//2, canvas_height//2, 
                        image=photo, 
                        tags="image"
                    )
                    
                    # Mantener referencia
                    self.current_editor_photo = photo
                    
                    # Configurar región de scroll
                    self.editor_canvas.configure(scrollregion=(0, 0, new_width, new_height))
                    
                    # Dibujar espacios existentes
                    self.redraw_spaces_in_editor()
                    
            except Exception as e:
                print(f"Error mostrando imagen en editor: {e}")
    
    def redraw_spaces_in_editor(self):
        """Redibuja los espacios en el canvas del editor"""
        if not hasattr(self, 'editor_canvas') or self.editor_canvas is None:
            return
            
        self.editor_canvas.delete("space")
        self.editor_canvas.delete("selected")
        
        for i, space in enumerate(self.spaces):
            x1, y1, x2, y2 = space.x, space.y, space.x + space.width, space.y + space.height
            
            # Color según estado
            if space == self.selected_space:
                color = ModernDarkTheme.COLORS['accent_yellow']
                width = 3
                tags = "selected"
            else:
                color = ModernDarkTheme.COLORS['accent_green']
                if i < len(self.analysis_results):
                    if hasattr(self.analysis_results[i], 'is_occupied') and self.analysis_results[i].is_occupied:
                        color = ModernDarkTheme.COLORS['accent_red']
                    elif not hasattr(self.analysis_results[i], 'is_occupied') and self.analysis_results[i]:
                        color = ModernDarkTheme.COLORS['accent_red']
                width = 2
                tags = "space"
            
            # Dibujar rectángulo
            self.editor_canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=color,
                width=width,
                fill='',
                tags=tags
            )
            
            # Agregar número del espacio
            self.editor_canvas.create_text(
                x1 + 5, y1 + 5,
                text=str(i + 1),
                fill=color,
                font=("Arial", 10, "bold"),
                anchor="nw",
                tags=tags
            )
    
    # Métodos de edición básicos (para funcionalidad mínima)
    def load_image_for_editor(self):
        """Carga una imagen para el editor"""
        filetypes = [("Imágenes", "*.jpg *.jpeg *.png *.bmp")]
        filepath = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=filetypes,
            initialdir=getattr(config, 'ASSETS_DIR', 'assets')
        )
        
        if filepath:
            frame = cv2.imread(filepath)
            if frame is not None:
                self.current_frame = frame
                self.update_video_display()
                self.refresh_editor_display()
                self.status_var.set(f"🖼️ Imagen cargada: {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", "No se pudo cargar la imagen")
    
    def start_drawing_mode(self):
        """Inicia el modo de dibujo"""
        self.drawing_mode = True
        self.selection_mode = False
        self.status_var.set("✏️ Modo dibujo activado - Arrastra para crear espacios")
        if hasattr(self, 'editor_info_label'):
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: DIBUJO ACTIVO"
            )
    
    def start_selection_mode(self):
        """Inicia el modo de selección"""
        self.selection_mode = True
        self.drawing_mode = False
        self.status_var.set("👆 Modo selección activado - Haz clic para seleccionar espacios")
        if hasattr(self, 'editor_info_label'):
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: SELECCIÓN"
            )
    
    def clear_all_spaces(self):
        """Elimina todos los espacios"""
        if messagebox.askyesno("Confirmar", "¿Eliminar todos los espacios definidos?"):
            self.spaces.clear()
            self.selected_space = None
            self.update_video_display()
            self.refresh_editor_display()
            self.status_var.set("🗑️ Todos los espacios eliminados")
            
            if hasattr(self, 'editor_info_label'):
                self.editor_info_label.configure(
                    text="Espacios definidos: 0 | Modo: Visualización"
                )
    
    # Métodos de eventos del canvas (básicos)
    def on_canvas_click(self, event):
        """Maneja clicks en el canvas"""
        if self.drawing_mode:
            x, y = self.editor_canvas.canvasx(event.x), self.editor_canvas.canvasy(event.y)
            self.drawing_start = (int(x), int(y))
    
    def on_canvas_drag(self, event):
        """Maneja arrastre en el canvas"""
        if self.drawing_mode and self.drawing_start:
            x, y = self.editor_canvas.canvasx(event.x), self.editor_canvas.canvasy(event.y)
            
            # Eliminar rectángulo temporal anterior
            self.editor_canvas.delete("temp_rect")
            
            # Dibujar nuevo rectángulo temporal
            self.editor_canvas.create_rectangle(
                self.drawing_start[0], self.drawing_start[1], x, y,
                outline=ModernDarkTheme.COLORS['accent_blue'],
                width=2,
                tags="temp_rect"
            )
    
    def on_canvas_release(self, event):
        """Maneja liberación del mouse"""
        if self.drawing_mode and self.drawing_start:
            x, y = self.editor_canvas.canvasx(event.x), self.editor_canvas.canvasy(event.y)
            
            # Calcular dimensiones del rectángulo
            x1, y1 = self.drawing_start
            w = abs(x - x1)
            h = abs(y - y1)
            
            # Validar tamaño mínimo
            if w > 20 and h > 20:
                # Crear nuevo espacio
                space_id = f"MANUAL_{len(self.spaces):03d}"
                new_space = ParkingSpace(
                    id=space_id,
                    x=int(min(x1, x)),
                    y=int(min(y1, y)),
                    width=int(w),
                    height=int(h)
                )
                self.spaces.append(new_space)
                
                self.status_var.set(f"✅ Espacio creado: {space_id}")
                
                # Actualizar visualización
                self.update_video_display()
                self.redraw_spaces_in_editor()
                
                if hasattr(self, 'editor_info_label'):
                    self.editor_info_label.configure(
                        text=f"Espacios definidos: {len(self.spaces)} | Modo: DIBUJO ACTIVO"
                    )
            
            # Limpiar
            self.editor_canvas.delete("temp_rect")
            self.drawing_start = None
    
    # Métodos de atajos de teclado (básicos)
    def copy_selected_space(self, event=None):
        """Copia el espacio seleccionado"""
        if self.selected_space:
            self.clipboard_spaces = [self.selected_space.copy()]
            self.status_var.set("📋 Espacio copiado")
    
    def paste_spaces(self, event=None):
        """Pega espacios del clipboard"""
        if self.clipboard_spaces:
            for space in self.clipboard_spaces:
                new_space = space.copy()
                new_space.x += 20  # Offset para evitar superposición
                new_space.y += 20
                new_space.id = f"PASTE_{len(self.spaces):03d}"
                self.spaces.append(new_space)
            
            self.update_video_display()
            self.refresh_editor_display()
            self.status_var.set(f"📋 {len(self.clipboard_spaces)} espacios pegados")
    
    def delete_selected_space(self, event=None):
        """Elimina el espacio seleccionado"""
        if self.selected_space and self.selected_space in self.spaces:
            self.spaces.remove(self.selected_space)
            self.selected_space = None
            self.update_video_display()
            self.refresh_editor_display()
            self.status_var.set("🗑️ Espacio eliminado")
    
    def undo_action(self, event=None):
        """Deshace la última acción"""
        if self.undo_stack:
            self.spaces = self.undo_stack.pop()
            self.update_video_display()
            self.refresh_editor_display()
            self.status_var.set("↶ Acción deshecha")
    
    def exit_all_modes(self, event=None):
        """Sale de todos los modos de edición"""
        self.drawing_mode = False
        self.selection_mode = False
        self.selected_space = None
        self.status_var.set("🚀 Modo visualización activado")
        
        if hasattr(self, 'editor_info_label'):
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: Visualización"
            )
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            self.is_analyzing = False
            if self.video_manager:
                self.video_manager.release()
        except:
            pass
        
        self.root.destroy()

# Función para inicializar la GUI moderna
def create_modern_gui(root: tk.Tk) -> ModernCarParkGUI:
    """Crea e inicializa la GUI moderna"""
    return ModernCarParkGUI(root)
