"""
GUI Moderna para CarPark Project v3.0
Interfaz completamente renovada con tema oscuro y funcionalidades mejoradas
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
from .legacy_detector import LegacySpaceEditor, LegacyOccupancyDetector, LegacyVideoProcessor
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
        self.space_editor = None
        
        # Componentes legacy mejorados
        self.legacy_space_editor = None
        self.legacy_detector = LegacyOccupancyDetector()
        self.legacy_video_processor = None
        
        # Estado de la aplicación
        self.spaces: List[ParkingSpace] = []
        self.current_frame = None
        self.analysis_results: List[OccupancyStatus] = []
        self.stats_history: List[AnalysisStats] = []
        self.is_analyzing = False
        
        # Variables de UI modernas
        self.main_notebook = None
        self.video_canvas = None
        self.stats_tree = None
        self.status_labels = {}
        self.progress_vars = {}
        
        # Variables para edición avanzada
        self.drawing_mode = False
        self.selection_mode = False
        self.drawing_start = None
        self.temp_rectangle = None
        self.selected_space = None
        self.dragging_space = False
        self.drag_offset = (0, 0)
        self.clipboard_spaces = []  # Para copy/paste
        self.undo_stack = []  # Para deshacer
        self.max_undo = 20  # Máximo de acciones para deshacer
        
        # Variables para manejo de escalado en el editor
        self.current_scale = 1.0
        self.image_offset_x = 0
        self.image_offset_y = 0
        self.original_image_size = None
        self.current_display_size = None
        
        self.setup_modern_ui()
        self.setup_bindings()
        self.start_status_updates()
    
    def setup_modern_window(self):
        """Configura la ventana principal con estilo moderno"""
        self.root.title("🚗 CarPark Professional v3.0")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 800)
        
        # Configurar tema oscuro
        self.style = ModernDarkTheme.configure_styles(self.root)
        
        # Configurar icono si existe
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
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
        
        # Agregar indicadores de estado en el título
        status_frame = ttk.Frame(title_frame)
        status_frame.pack(anchor=tk.E, padx=15, pady=(0, 15))
        
        # Indicador de conexión
        self.connection_status = ModernWidgets.create_status_indicator(
            status_frame, "Desconectado", "red"
        )
        self.connection_status.pack(side=tk.LEFT, padx=(0, 20))
        
        # Indicador de análisis
        self.analysis_status = ModernWidgets.create_status_indicator(
            status_frame, "Inactivo", "orange"
        )
        self.analysis_status.pack(side=tk.LEFT)
    
    def create_main_notebook(self, parent):
        """Crea el notebook principal con pestañas modernas"""
        self.main_notebook = ttk.Notebook(parent)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Pestaña 1: Monitor Principal
        self.create_monitor_tab()
        
        # Pestaña 2: Editor de Espacios
        self.create_editor_tab()
        
        # Pestaña 3: Análisis y Estadísticas
        self.create_analytics_tab()
        
        # Pestaña 4: Herramientas Legacy
        self.create_legacy_tab()
        
        # Pestaña 5: Configuración
        self.create_settings_tab()
        
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
        canvas_frame = ttk.Frame(video_card, style='Card.TFrame')
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
        ModernTooltip(load_video_btn, "Cargar archivo de video desde disco")
        
        load_camera_btn = ModernWidgets.create_action_button(
            row1, "Cámara Web", self.load_camera, "Action.TButton", "📹"
        )
        load_camera_btn.pack(side=tk.LEFT, padx=(0, 10))
        ModernTooltip(load_camera_btn, "Conectar cámara web")
        
        # Segunda fila de botones
        row2 = ttk.Frame(buttons_frame)
        row2.pack(fill=tk.X, pady=(0, 10))
        
        play_btn = ModernWidgets.create_action_button(
            row2, "Reproducir", self.toggle_analysis, "Success.TButton", "▶️"
        )
        play_btn.pack(side=tk.LEFT, padx=(0, 10))
        ModernTooltip(play_btn, "Iniciar/pausar análisis en tiempo real")
        
        snapshot_btn = ModernWidgets.create_action_button(
            row2, "Captura", self.take_snapshot, "Action.TButton", "📸"
        )
        snapshot_btn.pack(side=tk.LEFT)
        ModernTooltip(snapshot_btn, "Tomar captura de pantalla")
    
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
        self.analysis_method = tk.StringVar(value="adaptive")
        method_combo = ttk.Combobox(
            config_frame, 
            textvariable=self.analysis_method,
            values=["legacy", "adaptive", "background", "smart"],
            state="readonly"
        )
        method_combo.pack(fill=tk.X, pady=(0, 10))
        ModernTooltip(method_combo, "Selecciona el algoritmo de análisis")
        
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
            maximum=100,
            style='TProgressbar'
        )
        occupancy_progress.pack(fill=tk.X, pady=(5, 10))
    
    def create_spaces_controls(self, parent):
        """Crea controles para gestión de espacios"""
        # Botones de espacios
        detect_btn = ModernWidgets.create_action_button(
            parent, "Detectar Auto", self.detect_spaces, "Action.TButton", "🔍"
        )
        detect_btn.pack(fill=tk.X, pady=(0, 5))
        ModernTooltip(detect_btn, "Detectar espacios automáticamente")
        
        edit_btn = ModernWidgets.create_action_button(
            parent, "Editor Moderno", self.open_space_editor, "Action.TButton", "✏️"
        )
        edit_btn.pack(fill=tk.X, pady=(0, 5))
        ModernTooltip(edit_btn, "Abrir editor visual de espacios")
        
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        load_btn = ModernWidgets.create_action_button(
            parent, "Cargar Espacios", self.load_spaces, "TButton", "📂"
        )
        load_btn.pack(fill=tk.X, pady=(0, 5))
        
        save_btn = ModernWidgets.create_action_button(
            parent, "Guardar Espacios", self.save_spaces, "Success.TButton", "💾"
        )
        save_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Separador para análisis
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Controles de análisis en tiempo real
        analysis_label = ttk.Label(parent, text="Análisis en Tiempo Real", font=('Segoe UI', 10, 'bold'))
        analysis_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Botón de iniciar/pausar análisis
        self.analysis_btn = ModernWidgets.create_action_button(
            parent, "▶️ Iniciar Análisis", self.toggle_analysis, "Action.TButton", "🔄"
        )
        self.analysis_btn.pack(fill=tk.X, pady=(0, 5))
        ModernTooltip(self.analysis_btn, "Iniciar análisis automático en tiempo real")
        
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
            tools_row1, "Cargar Imagen", self.load_image_for_editor, "TButton", "🖼️"
        )
        load_img_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        load_spaces_btn = ModernWidgets.create_action_button(
            tools_row1, "Cargar Espacios", self.load_spaces, "TButton", "📂"
        )
        load_spaces_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_spaces_btn = ModernWidgets.create_action_button(
            tools_row1, "Guardar Espacios", self.save_spaces, "Success.TButton", "💾"
        )
        save_spaces_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Segunda fila de botones
        tools_row2 = ttk.Frame(tools_frame)
        tools_row2.pack(fill=tk.X)
        
        draw_btn = ModernWidgets.create_action_button(
            tools_row2, "Dibujar Espacios", self.start_drawing_mode, "Action.TButton", "✏️"
        )
        draw_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        select_btn = ModernWidgets.create_action_button(
            tools_row2, "Seleccionar", self.start_selection_mode, "TButton", "👆"
        )
        select_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = ModernWidgets.create_action_button(
            tools_row2, "Limpiar Todo", self.clear_all_spaces, "Warning.TButton", "🗑️"
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
        
        # Variables para el modo de dibujo
        self.drawing_mode = False
        self.drawing_start = None
        self.temp_rectangle = None
        
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
        
        # Scrollbars para el canvas
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.editor_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.editor_canvas.xview)
        self.editor_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars y canvas
        self.editor_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Variables para el modo de dibujo
        self.drawing_mode = False
        self.drawing_start = None
        self.temp_rectangle = None
        
        # Bindings para dibujo
        self.editor_canvas.bind("<Button-1>", self.on_canvas_click)
        self.editor_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.editor_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Binding para redimensionamiento del canvas del editor
        self.editor_canvas.bind('<Configure>', self.on_editor_canvas_resize)
        
        # Panel inferior - Información de espacios
        info_card = ModernWidgets.create_info_card(
            editor_frame, "Información de Espacios", "", "📊"
        )
        info_card.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        info_frame = ttk.Frame(info_card)
        info_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Información de espacios
        spaces_info = ttk.Label(info_frame, text="Espacios definidos: 0 | Modo: Visualización")
        spaces_info.pack(side=tk.LEFT)
        
        self.editor_info_label = spaces_info
    
    def create_analytics_tab(self):
        """Crea la pestaña de análisis y estadísticas"""
        analytics_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(analytics_frame, text="📈 Análisis")
        
        # Panel superior - Gráficos y resumen
        charts_card = ModernWidgets.create_info_card(
            analytics_frame, "Resumen de Ocupación", "", "📊"
        )
        charts_card.pack(fill=tk.X, padx=10, pady=10)
        
        # Frame para métricas
        metrics_frame = ttk.Frame(charts_card)
        metrics_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Métricas principales en columnas
        col1 = ttk.Frame(metrics_frame)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        col2 = ttk.Frame(metrics_frame)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        col3 = ttk.Frame(metrics_frame)
        col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Métricas en tiempo real
        self.create_metric_display(col1, "Total de Espacios", "total_metric", "🅿️")
        self.create_metric_display(col1, "Espacios Libres", "free_metric", "✅")
        
        self.create_metric_display(col2, "Espacios Ocupados", "occupied_metric", "🚫")
        self.create_metric_display(col2, "% de Ocupación", "percent_metric", "📊")
        
        self.create_metric_display(col3, "Tiempo de Análisis", "time_metric", "⏱️")
        self.create_metric_display(col3, "Estado Sistema", "status_metric", "💡")
        
        # Panel central - Datos históricos
        data_card = ModernWidgets.create_info_card(
            analytics_frame, "Historial de Datos", "", "📋"
        )
        data_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Frame para tabla con scrollbar
        table_frame = ttk.Frame(data_card)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Crear Treeview para datos con scrollbar
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.stats_tree = ttk.Treeview(
            tree_container,
            columns=('tiempo', 'total', 'libres', 'ocupados', 'porcentaje'),
            show='headings',
            height=8
        )
        
        # Configurar columnas
        self.stats_tree.heading('tiempo', text='Tiempo')
        self.stats_tree.heading('total', text='Total')
        self.stats_tree.heading('libres', text='Libres')
        self.stats_tree.heading('ocupados', text='Ocupados')
        self.stats_tree.heading('porcentaje', text='% Ocupación')
        
        self.stats_tree.column('tiempo', width=120, anchor='center')
        self.stats_tree.column('total', width=80, anchor='center')
        self.stats_tree.column('libres', width=80, anchor='center')
        self.stats_tree.column('ocupados', width=80, anchor='center')
        self.stats_tree.column('porcentaje', width=100, anchor='center')
        
        # Scrollbar para la tabla
        tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.stats_tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Botones de análisis
        buttons_frame = ttk.Frame(data_card)
        buttons_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        analyze_btn = ModernWidgets.create_action_button(
            buttons_frame, "Analizar Ahora", self.analyze_current_frame, "Success.TButton", "🔍"
        )
        analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = ModernWidgets.create_action_button(
            buttons_frame, "Exportar Datos", self.export_analytics_data, "TButton", "📤"
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_history_btn = ModernWidgets.create_action_button(
            buttons_frame, "Limpiar Historial", self.clear_analytics_history, "Warning.TButton", "🗑️"
        )
        clear_history_btn.pack(side=tk.LEFT)
    
    def create_metric_display(self, parent, title, var_name, icon):
        """Crea un display de métrica"""
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Icono y título
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text=f"{icon} {title}", font=('Segoe UI', 9, 'bold')).pack()
        
        # Valor
        value_var = tk.StringVar(value="0")
        setattr(self, var_name, value_var)
        
        value_label = ttk.Label(frame, textvariable=value_var, font=('Segoe UI', 16, 'bold'))
        value_label.pack(pady=(0, 10))
    
    def analyze_current_frame(self):
        """Analiza el frame actual"""
        if not self.spaces:
            messagebox.showwarning("Advertencia", "No hay espacios definidos")
            return
        
        if self.current_frame is None:
            messagebox.showwarning("Advertencia", "No hay imagen cargada")
            return
        
        try:
            # Realizar análisis
            self.analysis_results = self.analyzer.analyze_occupancy(self.current_frame, self.spaces)
            
            # Agregar a historial
            timestamp = datetime.now().strftime("%H:%M:%S")
            total_spaces = len(self.spaces)
            free_spaces = len([r for r in self.analysis_results if not r.is_occupied])
            occupied_spaces = total_spaces - free_spaces
            occupancy_percent = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
            
            # Insertar en tabla
            self.stats_tree.insert('', 0, values=(
                timestamp, total_spaces, free_spaces, occupied_spaces, f"{occupancy_percent:.1f}%"
            ))
            
            # Mantener solo los últimos 50 registros
            children = self.stats_tree.get_children()
            if len(children) > 50:
                for child in children[50:]:
                    self.stats_tree.delete(child)
            
            # Actualizar métricas
            self.update_analytics_metrics()
            
            # Redibujar espacios si estamos en el editor
            if hasattr(self, 'editor_canvas'):
                self.redraw_spaces_in_editor()
            
            self.status_var.set(f"📊 Análisis completado - {occupied_spaces}/{total_spaces} ocupados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis: {e}")
    
    def update_analytics_metrics(self):
        """Actualiza las métricas de análisis"""
        total_spaces = len(self.spaces)
        
        if self.analysis_results:
            free_spaces = len([r for r in self.analysis_results if not r.is_occupied])
            occupied_spaces = total_spaces - free_spaces
            occupancy_percent = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
        else:
            free_spaces = 0
            occupied_spaces = 0
            occupancy_percent = 0
        
        # Actualizar variables
        self.total_metric.set(str(total_spaces))
        self.free_metric.set(str(free_spaces))
        self.occupied_metric.set(str(occupied_spaces))
        self.percent_metric.set(f"{occupancy_percent:.1f}%")
        self.time_metric.set(datetime.now().strftime("%H:%M:%S"))
        
        # Estado del sistema
        if total_spaces == 0:
            status = "Sin espacios"
        elif not self.analysis_results:
            status = "Sin análisis"
        else:
            status = "Activo"
        self.status_metric.set(status)
    
    def export_analytics_data(self):
        """Exporta los datos de análisis"""
        if not self.stats_tree.get_children():
            messagebox.showwarning("Advertencia", "No hay datos para exportar")
            return
        
        filetypes = [("CSV files", "*.csv"), ("Archivos de texto", "*.txt")]
        filepath = filedialog.asksaveasfilename(
            title="Exportar Datos de Análisis",
            filetypes=filetypes,
            defaultextension=".csv"
        )
        
        if filepath:
            try:
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Escribir cabeceras
                    writer.writerow(['Tiempo', 'Total', 'Libres', 'Ocupados', 'Porcentaje'])
                    
                    # Escribir datos
                    for child in self.stats_tree.get_children():
                        values = self.stats_tree.item(child)['values']
                        writer.writerow(values)
                
                self.status_var.set(f"📤 Datos exportados a {os.path.basename(filepath)}")
                messagebox.showinfo("Éxito", "Datos exportados correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {e}")
    
    def clear_analytics_history(self):
        """Limpia el historial de análisis"""
        if messagebox.askyesno("Confirmar", "¿Eliminar todo el historial de datos?"):
            for child in self.stats_tree.get_children():
                self.stats_tree.delete(child)
            self.status_var.set("🗑️ Historial de análisis limpiado")
        
        # Configurar columnas
        self.stats_tree.heading('tiempo', text='Tiempo')
        self.stats_tree.heading('libres', text='Libres')
        self.stats_tree.heading('ocupados', text='Ocupados')
        self.stats_tree.heading('porcentaje', text='% Ocupación')
        
        self.stats_tree.column('tiempo', width=150)
        self.stats_tree.column('libres', width=80)
        self.stats_tree.column('ocupados', width=80)
        self.stats_tree.column('porcentaje', width=100)
        
        # Scrollbar para la tabla
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.stats_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_legacy_tab(self):
        """Crea la pestaña de herramientas legacy"""
        legacy_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(legacy_frame, text="🔧 Legacy Tools")
        
        # Descripción
        desc_card = ModernWidgets.create_info_card(
            legacy_frame, "Herramientas del Algoritmo Original", 
            "Mantiene la funcionalidad completa del código original con mejoras visuales", "🔧"
        )
        desc_card.pack(fill=tk.X, padx=10, pady=10)
        
        # Controles legacy en tarjetas separadas
        controls_frame = ttk.Frame(legacy_frame)
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Editor clásico
        editor_card = ModernWidgets.create_info_card(
            controls_frame, "Editor Clásico", 
            "Editor original con clic izquierdo/derecho para agregar/eliminar espacios", "✏️"
        )
        editor_card.pack(fill=tk.X, pady=(0, 10))
        
        editor_btn = ModernWidgets.create_action_button(
            editor_card, "Abrir Editor Clásico", self.open_legacy_editor, 
            "Action.TButton", "🖱️"
        )
        editor_btn.pack(padx=15, pady=(0, 15))
        
        # Análisis de video
        video_card = ModernWidgets.create_info_card(
            controls_frame, "Análisis de Video Legacy", 
            "Reproduce video con el algoritmo original de detección", "🎬"
        )
        video_card.pack(fill=tk.X, pady=(0, 10))
        
        video_btn = ModernWidgets.create_action_button(
            video_card, "Iniciar Video Legacy", self.start_legacy_video, 
            "Success.TButton", "▶️"
        )
        video_btn.pack(padx=15, pady=(0, 15))
        
        # Carga de imagen
        image_card = ModernWidgets.create_info_card(
            controls_frame, "Vista de Imagen", 
            "Carga una imagen para visualización y edición", "🖼️"
        )
        image_card.pack(fill=tk.X)
        
        image_btn = ModernWidgets.create_action_button(
            image_card, "Cargar Imagen", self.load_image_for_editor, 
            "Action.TButton", "📁"
        )
        image_btn.pack(padx=15, pady=(0, 15))
    
    def create_settings_tab(self):
        """Crea la pestaña de configuración"""
        settings_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(settings_frame, text="⚙️ Configuración")
        
        # Configuraciones del sistema
        system_card = ModernWidgets.create_info_card(
            settings_frame, "Configuración del Sistema", "", "⚙️"
        )
        system_card.pack(fill=tk.X, padx=10, pady=10)
        
        settings_content = ttk.Frame(system_card)
        settings_content.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Configuraciones de algoritmo
        ttk.Label(settings_content, text="Parámetros del Algoritmo Legacy:", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # Umbral de detección
        threshold_frame = ttk.Frame(settings_content)
        threshold_frame.pack(fill=tk.X, pady=5)
        ttk.Label(threshold_frame, text="Umbral de Detección:").pack(side=tk.LEFT)
        threshold_var = tk.IntVar(value=900)
        threshold_scale = ttk.Scale(threshold_frame, from_=500, to=1500, 
                                   variable=threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.pack(side=tk.RIGHT, padx=(10, 0), fill=tk.X, expand=True)
        
        # Tamaño de espacios
        size_frame = ttk.Frame(settings_content)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="Ancho de Espacio:").pack(side=tk.LEFT)
        width_var = tk.IntVar(value=107)
        width_spin = ttk.Spinbox(size_frame, from_=50, to=200, textvariable=width_var, width=10)
        width_spin.pack(side=tk.RIGHT, padx=(10, 0))
        
        size_frame2 = ttk.Frame(settings_content)
        size_frame2.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame2, text="Alto de Espacio:").pack(side=tk.LEFT)
        height_var = tk.IntVar(value=48)
        height_spin = ttk.Spinbox(size_frame2, from_=30, to=100, textvariable=height_var, width=10)
        height_spin.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botón para aplicar configuración
        apply_btn = ModernWidgets.create_action_button(
            settings_content, "Aplicar Configuración", self.apply_settings, 
            "Success.TButton", "✅"
        )
        apply_btn.pack(pady=20)
    
    def create_modern_status_bar(self, parent):
        """Crea una barra de estado moderna"""
        status_frame = ttk.Frame(parent, style='Card.TFrame')
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status principal
        self.status_var = tk.StringVar(value="✅ Sistema listo")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Información adicional
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Hora actual
        self.time_label = ttk.Label(info_frame, text="", style='Info.TLabel')
        self.time_label.pack(side=tk.RIGHT, padx=(20, 0))
        
        # FPS del video
        self.fps_label = ttk.Label(info_frame, text="FPS: 0", style='Info.TLabel')
        self.fps_label.pack(side=tk.RIGHT, padx=(20, 0))
    
    def start_status_updates(self):
        """Inicia las actualizaciones periódicas de estado"""
        self.update_time()
        self.update_stats()
    
    def update_time(self):
        """Actualiza la hora en la barra de estado"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.root.after(1000, self.update_time)
    
    def update_stats(self):
        """Actualiza las estadísticas en tiempo real"""
        # Actualizar estadísticas de espacios
        total_spaces = len(self.spaces)
        free_spaces = len([s for s in self.analysis_results if not s.is_occupied]) if self.analysis_results else 0
        occupied_spaces = total_spaces - free_spaces
        occupancy_percent = (occupied_spaces / total_spaces * 100) if total_spaces > 0 else 0
        
        # Actualizar etiquetas
        self.status_labels['total_spaces'].configure(text=str(total_spaces))
        self.status_labels['free_spaces'].configure(text=str(free_spaces))
        self.status_labels['occupied_spaces'].configure(text=str(occupied_spaces))
        self.status_labels['occupancy_percent'].configure(text=f"{occupancy_percent:.1f}%")
        
        # Actualizar barra de progreso
        self.progress_vars['occupancy'].set(occupancy_percent)
        
        # Programar siguiente actualización
        self.root.after(2000, self.update_stats)
    
    def setup_bindings(self):
        """Configura eventos y bindings"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Binding para redimensionamiento del canvas de video
        self.video_canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Atajos de teclado para el editor
        self.root.bind('<Control-c>', self.copy_selected_space)
        self.root.bind('<Control-v>', self.paste_spaces)
        self.root.bind('<Control-z>', self.undo_action)
        self.root.bind('<Delete>', self.delete_selected_space)
        self.root.bind('<Escape>', self.exit_all_modes)
        
        # Focus para que los atajos funcionen
        self.root.focus_set()
    
    def on_tab_changed(self, event):
        """Maneja el cambio de pestaña para actualizar visualización de forma robusta"""
        try:
            # Verificar que el notebook existe
            if not hasattr(self, 'main_notebook') or self.main_notebook is None:
                return
                
            # Obtener la pestaña actual de forma segura
            current_tab = self.main_notebook.select()
            if not current_tab:
                return
                
            tab_text = self.main_notebook.tab(current_tab, "text")
            
            # Si cambió a la pestaña principal (Dashboard/Monitor Principal)
            if "Dashboard" in tab_text or "Principal" in tab_text or "Monitor" in tab_text:
                # Usar delay más largo para asegurar que la pestaña se haya cargado completamente
                self.root.after(150, self.safe_update_main_panel)
                
            # Si cambió a la pestaña del editor y hay una imagen cargada
            elif "Editor de Espacios" in tab_text:
                # Pequeño delay para asegurar que el canvas esté listo
                self.root.after(150, self.safe_update_editor_panel)
                
        except Exception as e:
            print(f"Error en cambio de pestaña: {e}")
            # Si hay error, intentar recuperación después de un delay
            self.root.after(200, self.safe_fallback_update)
    
    def safe_update_main_panel(self):
        """Actualización segura específica para el panel principal"""
        try:
            # Verificar que tenemos frame y que el video canvas existe
            if self.current_frame is not None and hasattr(self, 'video_canvas') and self.video_canvas is not None:
                # Verificar que el canvas está visible y listo
                try:
                    self.video_canvas.update_idletasks()
                    if self.video_canvas.winfo_width() > 1:
                        self.update_video_display()
                    else:
                        # Canvas no está listo, programar otro intento
                        self.root.after(100, self.safe_update_video_display)
                except tk.TclError:
                    # Canvas no está listo, programar otro intento
                    self.root.after(100, self.safe_update_video_display)
            
            # Actualizar el status
            if hasattr(self, 'status_var'):
                self.status_var.set("📺 Panel principal actualizado")
                
        except Exception as e:
            print(f"Error en safe_update_main_panel: {e}")
    
    def safe_update_editor_panel(self):
        """Actualización segura específica para el panel del editor"""
        try:
            if self.current_frame is not None:
                self.refresh_editor_display()
                
        except Exception as e:
            print(f"Error en safe_update_editor_panel: {e}")
    
    def safe_fallback_update(self):
        """Método de recuperación cuando falla el cambio de pestaña"""
        try:
            # Solo mostrar un mensaje y no hacer nada más
            if hasattr(self, 'status_var'):
                self.status_var.set("⚠️ Error al cambiar pestaña - use botones de control")
        except:
            pass
    
    def safe_update_video_display(self):
        """Versión segura de update_video_display que no lanza errores críticos"""
        try:
            if self.current_frame is not None:
                self.update_video_display()
        except Exception as e:
            print(f"Error en safe_update_video_display: {e}")
            # Si hay error, intentar mostrar un mensaje en el status
            if hasattr(self, 'status_var'):
                self.status_var.set("⚠️ Error actualizando visualización")
    
    def refresh_editor_display(self):
        """Refresca la visualización del editor después de cambiar pestaña o cargar espacios"""
        if self.current_frame is not None:
            try:
                # Mostrar imagen en el editor (ya incluye redraw de espacios)
                self.display_image_in_editor()
                # Forzar actualización de la interfaz
                self.root.update_idletasks()
            except Exception as e:
                print(f"Error refrescando display del editor: {e}")
                
    def force_update_all_displays(self):
        """Fuerza la actualización de todos los displays después de cargar espacios"""
        try:
            # Actualizar el canvas de video si hay frame - usa la versión segura
            if self.current_frame is not None:
                self.safe_update_video_display()
                
            # Forzar actualización del editor
            self.refresh_editor_display()
            
            # Forzar redraw inmediato de espacios en el editor
            if hasattr(self, 'editor_canvas') and self.editor_canvas is not None:
                self.redraw_spaces_in_editor()
                
            # Actualizar múltiples veces para asegurar la visualización
            for i in range(3):
                try:
                    self.root.update_idletasks()
                    if i < 2:  # Solo hacer update completo las primeras dos veces
                        self.root.update()
                except Exception as e:
                    print(f"Error en update iteración {i}: {e}")
                    break
                    
            # Actualizar el status con información de los espacios cargados
            if hasattr(self, 'status_var'):
                self.status_var.set(f"✅ {len(self.spaces)} espacios cargados y visualizados")
                
            # Programar actualización adicional después de 200ms para asegurar sincronización
            self.root.after(200, self.delayed_display_update)
                
        except Exception as e:
            print(f"Error en force_update_all_displays: {e}")
            import traceback
            traceback.print_exc()
            
            # Intentar recuperación programando actualización
            self.root.after(300, self.safe_recovery_update)
    
    def delayed_display_update(self):
        """Actualización retrasada para asegurar sincronización después de cargar espacios"""
        try:
            # Verificar que el notebook existe antes de usarlo
            if not hasattr(self, 'main_notebook') or self.main_notebook is None:
                return
                
            # Verificar que estamos en la pestaña correcta
            current_tab = self.main_notebook.select()
            if current_tab:
                tab_text = self.main_notebook.tab(current_tab, "text")
                
                # Si estamos en el panel principal, actualizar video
                if "Principal" in tab_text or "Dashboard" in tab_text or "Monitor" in tab_text:
                    self.safe_update_video_display()
                    
                # Si estamos en el editor, actualizar editor
                elif "Editor" in tab_text:
                    self.refresh_editor_display()
                    
        except Exception as e:
            print(f"Error en delayed_display_update: {e}")
            # Solo intentar actualización básica si hay error
            self.safe_update_video_display()
    
    def safe_recovery_update(self):
        """Método de recuperación seguro cuando hay errores en la actualización"""
        try:
            # Intentar una actualización básica sin lanzar errores críticos
            if hasattr(self, 'video_canvas') and self.video_canvas is not None:
                self.video_canvas.update_idletasks()
                
            if hasattr(self, 'editor_canvas') and self.editor_canvas is not None:
                self.editor_canvas.update_idletasks()
                
            # Mostrar mensaje de estado
            if hasattr(self, 'status_var'):
                self.status_var.set("🔄 Recuperando visualización...")
                
        except Exception as e:
            print(f"Error en safe_recovery_update: {e}")

    def on_canvas_resize(self, event):
        """Maneja el redimensionamiento del canvas de video"""
        if self.current_frame is not None:
            self.update_video_display()
    
    def on_editor_canvas_resize(self, event):
        """Maneja el redimensionamiento del canvas del editor"""
        if self.current_frame is not None:
            # Programar actualización después de un breve delay para permitir 
            # que el redimensionamiento se complete
            self.root.after(50, self.display_image_in_editor)
    
    # Métodos de funcionalidad (adaptados de la GUI original)
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
                # Obtener primer frame
                frame = self.video_manager.get_frame()
                if frame is not None:
                    self.current_frame = frame
                    self.update_video_display()
                    # También actualizar el canvas del editor si existe
                    self.refresh_editor_display()
                    
                self.status_var.set(f"✅ Video cargado: {os.path.basename(filepath)}")
                
                # Actualizar indicador de conexión (buscar el label dentro del frame)
                for child in self.connection_status.winfo_children():
                    if isinstance(child, ttk.Label):
                        child.configure(text="Video Cargado")
                        break
            else:
                messagebox.showerror("Error", "No se pudo cargar el video")
    
    def load_camera(self):
        """Carga una cámara"""
        if self.video_manager.load_camera():
            # Obtener el primer frame de la cámara
            frame = self.video_manager.get_frame()
            if frame is not None:
                self.current_frame = frame
                self.update_video_display()
                # También actualizar el canvas del editor si existe
                self.refresh_editor_display()
            
            self.status_var.set("📹 Cámara conectada")
            
            # Actualizar indicador de conexión (buscar el label dentro del frame)
            for child in self.connection_status.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(text="Cámara Activa")
                    break
        else:
            messagebox.showerror("Error", "No se pudo conectar la cámara")
    
    def toggle_analysis(self):
        """Inicia/pausa el análisis en tiempo real"""
        if not self.is_analyzing:
            # Verificar que hay espacios definidos
            if not self.spaces:
                messagebox.showwarning(
                    "Sin espacios", 
                    "Primero debes definir espacios de estacionamiento.\n\n" +
                    "Opciones:\n" +
                    "• Usar 'Detectar Auto' para detección automática\n" +
                    "• Usar 'Editor Moderno' para dibujar manualmente\n" +
                    "• Usar 'Cargar Espacios' para cargar desde archivo"
                )
                return
            
            # Verificar que hay video/cámara
            if self.current_frame is None:
                messagebox.showwarning(
                    "Sin video", 
                    "Primero debes cargar un video o conectar una cámara.\n\n" +
                    "Ve a la pestaña 'Monitor Principal' y:\n" +
                    "• Carga un video\n" +
                    "• Conecta una cámara\n" +
                    "• Carga una imagen de referencia"
                )
                return
            
            # Iniciar análisis
            self.is_analyzing = True
            self.status_var.set("🔄 Análisis en tiempo real iniciado...")
            
            # Actualizar botón si existe
            if hasattr(self, 'analysis_btn'):
                self.analysis_btn.configure(text="⏸️ Pausar Análisis")
            
            # Actualizar estado si existe
            if hasattr(self, 'analysis_status_label'):
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
            
            # Actualizar botón si existe
            if hasattr(self, 'analysis_btn'):
                self.analysis_btn.configure(text="▶️ Iniciar Análisis")
            
            # Actualizar estado si existe
            if hasattr(self, 'analysis_status_label'):
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
                        # Usar el método seleccionado
                        method = self.analysis_method.get()
                        
                        if method == "adaptive":
                            self.analysis_results = self.analyzer.analyze_adaptive_threshold(frame, self.spaces)
                        elif method == "background":
                            self.analysis_results = self.analyzer.analyze_background_subtraction(frame, self.spaces)
                        elif method == "legacy":
                            self.analysis_results = self.analyzer.analyze_fixed_threshold(frame, self.spaces)
                        elif method == "smart":
                            self.analysis_results = self.analyzer.analyze_with_history(frame, self.spaces, "adaptive")
                        else:
                            # Fallback a legacy detector si no hay método válido
                            results, _ = self.legacy_detector.check_parking_spaces(frame, self.spaces)
                            self.analysis_results = results
                        
                        # Actualizar estadísticas en tiempo real
                        self.root.after(0, self.update_real_time_stats)
                    
                    # Actualizar display
                    self.root.after(0, self.update_video_display)
                
                # Controlar velocidad de análisis
                time.sleep(0.5)  # Análisis cada 500ms para mejor rendimiento
                
            except Exception as e:
                print(f"Error en analysis_loop: {e}")
                time.sleep(1)  # Esperar más tiempo si hay error
    
    def update_real_time_stats(self):
        """Actualiza las estadísticas en tiempo real"""
        if self.analysis_results:
            # Calcular estadísticas
            total_spaces = len(self.analysis_results)
            
            # Contar ocupados dependiendo del tipo de resultado
            if hasattr(self.analysis_results[0], 'is_occupied'):
                # Resultado moderno (OccupancyStatus)
                occupied_count = sum(1 for result in self.analysis_results if result.is_occupied)
            else:
                # Resultado legacy (boolean)
                occupied_count = sum(1 for result in self.analysis_results if result)
            
            free_count = total_spaces - occupied_count
            occupancy_percent = (occupied_count / total_spaces * 100) if total_spaces > 0 else 0
            
            # Actualizar labels si existen
            if hasattr(self, 'status_labels'):
                self.status_labels['total_spaces'].configure(text=str(total_spaces))
                self.status_labels['free_spaces'].configure(text=str(free_count))
                self.status_labels['occupied_spaces'].configure(text=str(occupied_count))
                self.status_labels['occupancy_percent'].configure(text=f"{occupancy_percent:.1f}%")
                
                # Actualizar barra de progreso si existe
                if hasattr(self, 'progress_vars'):
                    self.progress_vars['occupancy'].set(occupancy_percent)
    
    def update_video_display(self):
        """Actualiza la visualización del video con manejo robusto de errores"""
        if self.current_frame is None:
            return
            
        # Verificar que el video canvas existe y está listo
        if not hasattr(self, 'video_canvas') or self.video_canvas is None:
            return
        
        try:
            # Obtener dimensiones del canvas de forma segura
            self.video_canvas.update_idletasks()
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            # Si el canvas aún no está listo, usar valores por defecto
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 800
                canvas_height = 600
            
            # Crear una copia del frame para modificar
            display_frame = self.current_frame.copy()
            
            # Dibujar espacios si existen
            if self.spaces:
                display_frame = self.draw_spaces_on_frame(display_frame)
            
            # Redimensionar frame manteniendo proporción
            height, width = display_frame.shape[:2]
            scale = min(canvas_width / width, canvas_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Validar dimensiones antes de redimensionar
            if new_width > 0 and new_height > 0:
                frame_resized = cv2.resize(display_frame, (new_width, new_height))
                
                # Convertir a RGB para Tkinter
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
                
                # Mantener referencia para evitar garbage collection
                self.current_video_photo = photo
            
        except Exception as e:
            print(f"Error actualizando video display: {e}")
            import traceback
            traceback.print_exc()
            
            # Mostrar mensaje de error en el canvas de forma segura
            try:
                if hasattr(self, 'video_canvas') and self.video_canvas is not None:
                    self.video_canvas.delete("all")
                    canvas_w = self.video_canvas.winfo_width()
                    canvas_h = self.video_canvas.winfo_height()
                    
                    if canvas_w > 1 and canvas_h > 1:
                        self.video_canvas.create_text(
                            canvas_w // 2,
                            canvas_h // 2,
                            text="Error al mostrar video\nRevise la consola para detalles",
                            fill="white",
                            font=("Arial", 12),
                            justify="center"
                        )
            except Exception as canvas_error:
                print(f"Error adicional en canvas: {canvas_error}")
    
    def draw_spaces_on_frame(self, frame):
        """Dibuja los espacios en el frame y retorna el frame modificado"""
        try:
            for i, space in enumerate(self.spaces):
                # Determinar color según estado
                if i < len(self.analysis_results):
                    if hasattr(self.analysis_results[i], 'is_occupied'):
                        # Resultado moderno (OccupancyStatus)
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
            
            return frame
            
        except Exception as e:
            print(f"Error dibujando espacios en frame: {e}")
            return frame  # Retornar frame original si hay error
    
    def take_snapshot(self):
        """Toma una captura de pantalla"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)
            self.status_var.set(f"📸 Captura guardada: {filename}")
        else:
            messagebox.showwarning("Advertencia", "No hay video cargado")
    
    # Métodos heredados y adaptados de la GUI original
    def detect_spaces(self):
        """Detecta espacios automáticamente"""
        if self.current_frame is not None:
            self.spaces = self.detector.detect_spaces_contours(self.current_frame)
            self.status_var.set(f"🔍 Detectados {len(self.spaces)} espacios")
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
            # Intentar cargar como JSON primero
            if filepath.endswith('.json'):
                spaces = FileManager.load_spaces_json(filepath)
                if spaces:
                    self.spaces = spaces
                    self.status_var.set(f"📂 Cargados {len(spaces)} espacios desde JSON")
                    # Actualizar visualización inmediatamente en ambos canvas
                    self.force_update_all_displays()
                else:
                    messagebox.showerror("Error", "No se pudieron cargar los espacios JSON")
            else:
                # Intentar cargar como archivo legacy (pickle)
                try:
                    import pickle
                    with open(filepath, 'rb') as f:
                        positions = pickle.load(f)
                    
                    # Convertir posiciones legacy a espacios modernos
                    spaces = []
                    # Dimensiones por defecto del formato legacy
                    default_width = 107
                    default_height = 48
                    
                    for i, pos in enumerate(positions):
                        if len(pos) >= 2:
                            if len(pos) == 2:
                                # Formato legacy: solo (x, y)
                                x, y = pos
                                w, h = default_width, default_height
                            else:
                                # Formato extendido: (x, y, w, h, ...)
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
                        # Actualizar visualización inmediatamente en ambos canvas
                        self.force_update_all_displays()
                    else:
                        messagebox.showwarning("Advertencia", "No se encontraron espacios en el archivo")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")
    
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
                self.status_var.set("💾 Espacios guardados")
            else:
                messagebox.showerror("Error", "No se pudieron guardar los espacios")
    
    # Métodos legacy adaptados
    def open_legacy_editor(self):
        """Abre el editor legacy"""
        filetypes = [("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
        image_path = filedialog.askopenfilename(
            title="Seleccionar Imagen para Editor Legacy",
            filetypes=filetypes,
            initialdir=getattr(config, 'ASSETS_DIR', 'assets')
        )
        
        if image_path:
            try:
                self.legacy_space_editor = LegacySpaceEditor(
                    image_path=image_path,
                    positions_file="CarParkPos"
                )
                
                messagebox.showinfo(
                    "Editor Legacy",
                    "Se abrirá el editor clásico de espacios.\n\n"
                    "Controles:\n"
                    "• Clic izquierdo: Agregar espacio\n"
                    "• Clic derecho: Eliminar espacio\n"
                    "• 'q': Salir\n"
                    "• 's': Cambiar tamaño de espacios"
                )
                
                def run_editor():
                    self.legacy_space_editor.start_editing(self.on_legacy_spaces_updated)
                
                threading.Thread(target=run_editor, daemon=True).start()
                self.status_var.set("🔧 Editor legacy iniciado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al iniciar editor legacy: {e}")
    
    def start_legacy_video(self):
        """Inicia video legacy"""
        if not os.path.exists("CarParkPos"):
            messagebox.showwarning(
                "Advertencia",
                "No se encontró el archivo CarParkPos.\n"
                "Usa primero el 'Editor Clásico' para definir espacios."
            )
            return
        
        filetypes = [("Videos", "*.mp4 *.avi *.mov *.mkv *.wmv")]
        video_path = filedialog.askopenfilename(
            title="Seleccionar Video para Análisis Legacy",
            filetypes=filetypes,
            initialdir=getattr(config, 'ASSETS_DIR', 'assets')
        )
        
        if video_path:
            try:
                self.legacy_video_processor = LegacyVideoProcessor(
                    video_path=video_path,
                    positions_file="CarParkPos"
                )
                
                messagebox.showinfo(
                    "Video Legacy",
                    "Se iniciará la reproducción con detección legacy.\n\n"
                    "Controles:\n"
                    "• 'q': Salir\n"
                    "• ESPACIO: Pausar/Reanudar\n"
                    "• 'r': Reiniciar video"
                )
                
                def run_video():
                    self.legacy_video_processor.play_video()
                
                threading.Thread(target=run_video, daemon=True).start()
                self.status_var.set("🎬 Video legacy iniciado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al iniciar video legacy: {e}")
    
    def display_image_in_editor(self):
        """Muestra la imagen actual en el canvas del editor con escalado correcto"""
        if self.current_frame is not None and hasattr(self, 'editor_canvas') and self.editor_canvas is not None:
            try:
                # Obtener dimensiones originales de la imagen
                height, width = self.current_frame.shape[:2]
                self.original_image_size = (width, height)
                
                # Actualizar el canvas para obtener dimensiones reales
                self.editor_canvas.update_idletasks()
                canvas_width = self.editor_canvas.winfo_width()
                canvas_height = self.editor_canvas.winfo_height()
                
                # Usar dimensiones por defecto si el canvas no está listo
                if canvas_width <= 1 or canvas_height <= 1:
                    canvas_width = 800
                    canvas_height = 600
                
                # Calcular escala para ajustar imagen
                scale_w = canvas_width / width
                scale_h = canvas_height / height
                self.current_scale = min(scale_w, scale_h, 1.0)  # No agrandar
                
                new_width = int(width * self.current_scale)
                new_height = int(height * self.current_scale)
                self.current_display_size = (new_width, new_height)
                
                # Calcular offset para centrar la imagen
                self.image_offset_x = (canvas_width - new_width) // 2
                self.image_offset_y = (canvas_height - new_height) // 2
                
                # Mantener compatibilidad con código existente
                self.editor_scale = self.current_scale
                self.editor_offset_x = self.image_offset_x
                self.editor_offset_y = self.image_offset_y
                
                if new_width > 0 and new_height > 0:
                    resized_frame = cv2.resize(self.current_frame, (new_width, new_height))
                    
                    # Convertir BGR a RGB para Tkinter
                    if len(resized_frame.shape) == 3:
                        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                    
                    # Convertir a formato Tkinter
                    image_pil = Image.fromarray(resized_frame)
                    photo = ImageTk.PhotoImage(image_pil)
                    
                    # Mostrar en canvas
                    self.editor_canvas.delete("image")
                    self.editor_canvas.create_image(
                        self.image_offset_x, self.image_offset_y, 
                        image=photo, 
                        anchor="nw",
                        tags="image"
                    )
                    
                    # Mantener referencia para evitar garbage collection
                    self.current_editor_photo = photo
                    
                    # Configurar región de scroll
                    self.editor_canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
                    
                    # Dibujar espacios existentes con la nueva escala
                    self.redraw_spaces_in_editor()
                    
                    # Actualizar info
                    if hasattr(self, 'editor_info_label'):
                        mode_text = "SELECCIÓN" if self.selection_mode else ("Dibujo ACTIVO" if self.drawing_mode else "Visualización")
                        self.editor_info_label.configure(
                            text=f"Espacios definidos: {len(self.spaces)} | Modo: {mode_text} | Escala: {self.current_scale:.2f}"
                        )
            except Exception as e:
                print(f"Error mostrando imagen en editor: {e}")
                import traceback
                traceback.print_exc()
    
    def redraw_spaces_in_editor(self):
        """Redibuja los espacios en el canvas del editor"""
        if not hasattr(self, 'editor_canvas') or self.editor_canvas is None:
            return
            
        self.editor_canvas.delete("space")
        self.editor_canvas.delete("selected")
        
        # Verificar que tenemos información de escala
        if not hasattr(self, 'editor_scale'):
            return
        
        for i, space in enumerate(self.spaces):
            # Aplicar escala y offset a las coordenadas originales del espacio
            x1_scaled = int(space.x * self.editor_scale) + self.editor_offset_x
            y1_scaled = int(space.y * self.editor_scale) + self.editor_offset_y
            x2_scaled = int((space.x + space.width) * self.editor_scale) + self.editor_offset_x
            y2_scaled = int((space.y + space.height) * self.editor_scale) + self.editor_offset_y
            
            # Color según estado
            if space == self.selected_space:
                # Espacio seleccionado
                color = ModernDarkTheme.COLORS['accent_yellow']
                width = 3
                tags = "selected"
            else:
                # Color según análisis si está disponible
                color = ModernDarkTheme.COLORS['accent_green']
                if i < len(self.analysis_results):
                    if hasattr(self.analysis_results[i], 'is_occupied'):
                        if self.analysis_results[i].is_occupied:
                            color = ModernDarkTheme.COLORS['accent_red']
                    else:
                        # Resultado legacy (boolean)
                        if self.analysis_results[i]:
                            color = ModernDarkTheme.COLORS['accent_red']
                width = 2
                tags = "space"
            
            # Dibujar rectángulo escalado
            rect_id = self.editor_canvas.create_rectangle(
                x1_scaled, y1_scaled, x2_scaled, y2_scaled,
                outline=color,
                width=width,
                fill='',
                tags=tags
            )
            
            # Agregar número del espacio escalado
            text_id = self.editor_canvas.create_text(
                x1_scaled + 5, y1_scaled + 5,
                text=str(i + 1),  # Usar i+1 para que empiece en 1
                fill=color,
                font=("Arial", max(8, int(10 * self.editor_scale)), "bold"),
                anchor="nw",
                tags=tags
            )
    
    def clear_all_spaces(self):
        """Elimina todos los espacios"""
        if messagebox.askyesno("Confirmar", "¿Eliminar todos los espacios definidos?"):
            # Guardar estado para undo
            self.save_state_for_undo()
            
            self.spaces.clear()
            self.selected_space = None
            self.editor_canvas.delete("space")
            self.editor_canvas.delete("selected")
            self.status_var.set("🗑️ Todos los espacios eliminados")
            
            # Actualizar información
            if hasattr(self, 'editor_info_label'):
                mode_text = "SELECCIÓN" if self.selection_mode else ("Dibujo ACTIVO" if self.drawing_mode else "Visualización")
                self.editor_info_label.configure(
                    text=f"Espacios definidos: 0 | Modo: {mode_text}"
                )
    
    def load_image_for_editor(self):
        """Carga una imagen específicamente para el editor"""
        filetypes = [("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        filepath = filedialog.askopenfilename(
            title="Seleccionar Imagen para Editor",
            filetypes=filetypes,
            initialdir=getattr(config, 'ASSETS_DIR', 'assets')
        )
        
        if filepath:
            try:
                # Cargar imagen con cv2
                image = cv2.imread(filepath)
                if image is not None:
                    self.current_frame = image
                    self.display_image_in_editor()
                    # También actualizar el monitor principal
                    self.update_video_display()
                    self.status_var.set(f"🖼️ Imagen cargada: {os.path.basename(filepath)}")
                else:
                    messagebox.showerror("Error", "No se pudo cargar la imagen")
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando imagen: {e}")
    
    def start_drawing_mode(self):
        """Inicia el modo de dibujo"""
        self.drawing_mode = True
        self.selection_mode = False
        self.selected_space = None
        self.editor_canvas.configure(cursor="crosshair")
        self.status_var.set("✏️ Modo dibujo activado")
        self.redraw_spaces_in_editor()
        
        # Actualizar información
        if hasattr(self, 'editor_info_label'):
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: Dibujo ACTIVO"
            )
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Convierte coordenadas del canvas a coordenadas de la imagen original"""
        if not hasattr(self, 'editor_scale') or not hasattr(self, 'editor_offset_x'):
            return canvas_x, canvas_y
        
        # Restar el offset y dividir por la escala
        image_x = (canvas_x - self.editor_offset_x) / self.editor_scale
        image_y = (canvas_y - self.editor_offset_y) / self.editor_scale
        
        return int(image_x), int(image_y)
    
    def image_to_canvas_coords(self, image_x, image_y):
        """Convierte coordenadas de la imagen original a coordenadas del canvas"""
        if not hasattr(self, 'editor_scale') or not hasattr(self, 'editor_offset_x'):
            return image_x, image_y
        
        # Aplicar escala y agregar offset
        canvas_x = int(image_x * self.editor_scale) + self.editor_offset_x
        canvas_y = int(image_y * self.editor_scale) + self.editor_offset_y
        
        return canvas_x, canvas_y
    
    def find_space_at_point(self, canvas_x, canvas_y):
        """Encuentra el espacio en las coordenadas dadas del canvas"""
        # Convertir coordenadas del canvas a coordenadas de imagen
        image_x, image_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        
        for space in self.spaces:
            if (space.x <= image_x <= space.x + space.width and
                space.y <= image_y <= space.y + space.height):
                return space
        return None
    
    def save_state_for_undo(self):
        """Guarda el estado actual para poder deshacerlo"""
        # Copiar espacios actuales
        current_state = [space.copy() for space in self.spaces]
        self.undo_stack.append(current_state)
        
        # Limitar el tamaño del stack
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
    
    def start_selection_mode(self):
        """Inicia el modo de selección"""
        self.selection_mode = True
        self.drawing_mode = False
        self.selected_space = None
        self.editor_canvas.configure(cursor="hand2")
        self.status_var.set("👆 Modo selección activado")
        self.redraw_spaces_in_editor()
        
        # Actualizar información
        if hasattr(self, 'editor_info_label'):
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: SELECCIÓN"
            )
    
    def copy_selected_space(self, event=None):
        """Copia el espacio seleccionado al clipboard"""
        if self.selected_space is not None:
            self.clipboard_spaces = [self.selected_space.copy()]
            self.status_var.set(f"📋 Espacio {self.selected_space.id} copiado")
        elif self.spaces:
            # Si no hay selección, copiar todos los espacios
            self.clipboard_spaces = [space.copy() for space in self.spaces]
            self.status_var.set(f"📋 {len(self.spaces)} espacios copiados")
        else:
            self.status_var.set("⚠️ No hay espacios para copiar")
    
    def paste_spaces(self, event=None):
        """Pega espacios del clipboard"""
        if not self.clipboard_spaces:
            self.status_var.set("⚠️ Clipboard vacío")
            return
        
        # Guardar estado para undo
        self.save_state_for_undo()
        
        # Calcular offset para evitar solapamiento
        offset_x, offset_y = 20, 20
        
        pasted_count = 0
        for space in self.clipboard_spaces:
            new_space = ParkingSpace(
                id=str(len(self.spaces)),
                x=space.x + offset_x,
                y=space.y + offset_y,
                width=space.width,
                height=space.height
            )
            self.spaces.append(new_space)
            pasted_count += 1
        
        self.redraw_spaces_in_editor()
        self.status_var.set(f"📋 {pasted_count} espacios pegados")
        
        # Actualizar información
        if hasattr(self, 'editor_info_label'):
            mode_text = "SELECCIÓN" if self.selection_mode else ("Dibujo ACTIVO" if self.drawing_mode else "Visualización")
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: {mode_text}"
            )
    
    def delete_selected_space(self, event=None):
        """Elimina el espacio seleccionado"""
        if self.selected_space is not None:
            # Guardar estado para undo
            self.save_state_for_undo()
            
            # Eliminar espacio
            if self.selected_space in self.spaces:
                self.spaces.remove(self.selected_space)
                
                # Renumerar IDs
                for i, space in enumerate(self.spaces):
                    space.id = str(i)
                
                self.selected_space = None
                self.redraw_spaces_in_editor()
                self.status_var.set("🗑️ Espacio eliminado")
                
                # Actualizar información
                if hasattr(self, 'editor_info_label'):
                    mode_text = "SELECCIÓN" if self.selection_mode else ("Dibujo ACTIVO" if self.drawing_mode else "Visualización")
                    self.editor_info_label.configure(
                        text=f"Espacios definidos: {len(self.spaces)} | Modo: {mode_text}"
                    )
        else:
            self.status_var.set("⚠️ No hay espacio seleccionado")
    
    def undo_action(self, event=None):
        """Deshace la última acción"""
        if self.undo_stack:

            # Restaurar estado anterior
            previous_state = self.undo_stack.pop()
            self.spaces = [space.copy() for space in previous_state]
            self.selected_space = None
            self.redraw_spaces_in_editor()
            self.status_var.set(f"↶ Acción deshecha ({len(self.undo_stack)} en historial)")
            
            # Actualizar información
            if hasattr(self, 'editor_info_label'):
                mode_text = "SELECCIÓN" if self.selection_mode else ("Dibujo ACTIVO" if self.drawing_mode else "Visualización")
                self.editor_info_label.configure(
                    text=f"Espacios definidos: {len(self.spaces)} | Modo: {mode_text}"
                )
        else:
            self.status_var.set("⚠️ No hay acciones para deshacer")
    
    def exit_all_modes(self, event=None):
        """Sale de todos los modos de edición"""
        self.drawing_mode = False
        self.selection_mode = False
        self.selected_space = None
        self.dragging_space = False
        if hasattr(self, 'editor_canvas') and self.editor_canvas:
            self.editor_canvas.configure(cursor="arrow")
            self.redraw_spaces_in_editor()
        self.status_var.set("👁️ Modo visualización")
        
        # Actualizar información
        if hasattr(self, 'editor_info_label'):
            self.editor_info_label.configure(
                text=f"Espacios definidos: {len(self.spaces)} | Modo: Visualización"
            )
    
    def on_canvas_click(self, event):
        """Maneja el clic en el canvas del editor con coordenadas escaladas correctas"""
        if self.selection_mode:
            # Convertir coordenadas de canvas a coordenadas de imagen
            img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
            
            # Buscar espacio en la posición del clic (coordenadas de imagen)
            clicked_space = self.find_space_at_point(img_x, img_y)
            if clicked_space:
                self.selected_space = clicked_space
                self.dragging_space = True
                
                # Calcular offset en coordenadas de canvas para el drag
                canvas_x, canvas_y = self.image_to_canvas_coords(clicked_space.x, clicked_space.y)
                self.drag_offset = (event.x - canvas_x, event.y - canvas_y)
                
                self.redraw_spaces_in_editor()
                self.status_var.set(f"👆 Espacio {clicked_space.id or len(self.spaces)} seleccionado")
            else:
                self.selected_space = None
                self.redraw_spaces_in_editor()
                self.status_var.set("👆 Modo selección activo")
        elif self.drawing_mode:
            # Guardar estado para undo antes de crear nuevo espacio
            self.save_state_for_undo()
            
            # Convertir coordenadas a imagen para el inicio del dibujo
            img_x, img_y = self.canvas_to_image_coords(event.x, event.y)
            self.drawing_start = (img_x, img_y)
            
            # Limpiar rectángulo temporal previo
            self.editor_canvas.delete("temp")
    
    def on_canvas_drag(self, event):
        """Maneja el arrastre en el canvas del editor con coordenadas escaladas"""
        if self.selection_mode and self.dragging_space and self.selected_space:
            # Convertir coordenadas de canvas a imagen
            img_x, img_y = self.canvas_to_image_coords(event.x - self.drag_offset[0], event.y - self.drag_offset[1])
            
            # Asegurar que no se salga de la imagen original
            if self.original_image_size is not None:
                orig_w, orig_h = self.original_image_size
                img_x = max(0, min(img_x, orig_w - self.selected_space.width))
                img_y = max(0, min(img_y, orig_h - self.selected_space.height))
            else:
                img_x = max(0, img_x)
                img_y = max(0, img_y)
            
            # Actualizar posición en coordenadas de imagen
            self.selected_space.x = int(img_x)
            self.selected_space.y = int(img_y)
            
            # Redibujar inmediatamente para feedback visual
            self.redraw_spaces_in_editor()
            
            # Forzar actualización del canvas
            self.editor_canvas.update_idletasks()
            
        elif self.drawing_mode and self.drawing_start:
            # Limpiar rectángulo temporal previo
            self.editor_canvas.delete("temp")
            
            # Convertir coordenadas actuales a imagen
            img_x2, img_y2 = self.canvas_to_image_coords(event.x, event.y)
            
            # Convertir coordenadas de inicio e fin a canvas para visualización
            canvas_x1, canvas_y1 = self.image_to_canvas_coords(self.drawing_start[0], self.drawing_start[1])
            canvas_x2, canvas_y2 = self.image_to_canvas_coords(img_x2, img_y2)
            
            self.temp_rectangle = self.editor_canvas.create_rectangle(
                canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                outline=ModernDarkTheme.COLORS['accent_blue'],
                width=2,
                fill='',
                tags="temp"
            )
    
    def on_canvas_release(self, event):
        """Maneja la liberación del clic en el canvas del editor con coordenadas escaladas"""
        if self.selection_mode and self.dragging_space:
            self.dragging_space = False
            if self.selected_space:
                self.status_var.set(f"👆 Espacio {self.selected_space.id or len(self.spaces)} movido")
            
        elif self.drawing_mode and self.drawing_start:
            # Convertir coordenadas finales a imagen
            img_x2, img_y2 = self.canvas_to_image_coords(event.x, event.y)
            
            x1, y1 = self.drawing_start  # Ya están en coordenadas de imagen
            x2, y2 = img_x2, img_y2
            
            # Asegurar que x1,y1 sea la esquina superior izquierda
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            
            # Validar tamaño mínimo en coordenadas de imagen
            width = max_x - min_x
            height = max_y - min_y
            if width > 20 and height > 15:  # Tamaño mínimo en píxeles de imagen original
                # Crear nuevo espacio en coordenadas de imagen
                new_space = ParkingSpace(
                    id=str(len(self.spaces)),
                    x=int(min_x),
                    y=int(min_y),
                    width=int(width),
                    height=int(height)
                )
                self.spaces.append(new_space)
                
                # Actualizar interfaz
                if hasattr(self, 'editor_info_label'):
                    self.editor_info_label.configure(text=f"Espacios definidos: {len(self.spaces)} | Modo: Dibujo ACTIVO")
                self.status_var.set(f"✅ Espacio {len(self.spaces)} creado")
                
                # Redibujar
                self.redraw_spaces_in_editor()
            else:
                self.status_var.set("⚠️ Espacio muy pequeño, intente de nuevo")
                
            # Limpiar rectángulo temporal
            self.editor_canvas.delete("temp")
            self.drawing_start = None
            
            # Limpiar temporal
            self.editor_canvas.delete("temp")
            self.drawing_start = None
    
    def apply_settings(self):
        """Aplica la configuración (placeholder)"""
        self.status_var.set("⚙️ Configuración aplicada")
    
    def on_legacy_spaces_updated(self, spaces):
        """Callback cuando se actualizan espacios desde el editor legacy"""
        self.spaces = spaces
        self.redraw_spaces_in_editor()
        self.status_var.set(f"✅ Espacios actualizados desde editor legacy: {len(spaces)}")
    
    def on_closing(self):
        """Limpia recursos al cerrar"""
        self.is_analyzing = False
        self.video_manager.stop_capture()
        self.video_manager.release()
        self.root.destroy()

# Función para inicializar la GUI moderna
def create_modern_gui(root: tk.Tk) -> ModernCarParkGUI:
    """Crea e inicializa la GUI moderna"""
    return ModernCarParkGUI(root)
