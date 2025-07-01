"""
Editor visual de espacios de estacionamiento
"""
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from typing import List, Optional, Callable, Tuple
from .models import ParkingSpace

class SpaceEditor:
    """Editor visual para espacios de estacionamiento"""
    
    def __init__(self, parent: tk.Tk, frame: np.ndarray, initial_spaces: List[ParkingSpace]):
        self.parent = parent
        self.frame = frame.copy()
        self.spaces = initial_spaces.copy() if initial_spaces else []
        self.callback: Optional[Callable] = None
        
        # Estado del editor
        self.current_mode = "select"  # select, draw, move, resize, delete
        self.selected_space = None
        self.drawing_start = None
        self.drawing_current = None
        self.is_drawing = False
        
        # Ventana del editor
        self.window = None
        self.canvas = None
        self.photo = None
        
        # Variables de UI
        self.mode_var = tk.StringVar(value="select")
        self.info_var = tk.StringVar(value="Listo")
        
    def show(self, callback: Callable[[List[ParkingSpace]], None]):
        """Muestra el editor"""
        self.callback = callback
        self.create_window()
        self.setup_ui()
        self.update_display()
        
    def create_window(self):
        """Crea la ventana del editor"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Editor de Espacios - CarPark")
        self.window.geometry("1200x800")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configurar cierre
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_ui(self):
        """Configura la interfaz del editor"""
        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior - Herramientas
        self.setup_toolbar(main_frame)
        
        # Panel central - Canvas
        self.setup_canvas(main_frame)
        
        # Panel inferior - Estado e información
        self.setup_status_bar(main_frame)
        
    def setup_toolbar(self, parent):
        """Configura la barra de herramientas"""
        toolbar = ttk.LabelFrame(parent, text="Herramientas", padding=5)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para herramientas principales
        tools_frame = ttk.Frame(toolbar)
        tools_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Modos de edición
        modes = [
            ("Seleccionar", "select"),
            ("Dibujar", "draw"),
            ("Mover", "move"),
            ("Redimensionar", "resize"),
            ("Eliminar", "delete")
        ]
        
        for text, mode in modes:
            btn = ttk.Radiobutton(tools_frame, text=text, 
                                 variable=self.mode_var, value=mode,
                                 command=self.on_mode_change)
            btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame para acciones
        actions_frame = ttk.Frame(toolbar)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="Detectar Auto", 
                  command=self.auto_detect).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Limpiar Todo", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Aplicar", 
                  command=self.apply_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="Cancelar", 
                  command=self.cancel_changes).pack(side=tk.LEFT)
        
    def setup_canvas(self, parent):
        """Configura el canvas principal"""
        canvas_frame = ttk.LabelFrame(parent, text="Editor Visual", padding=5)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas con scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg='black', cursor='crosshair')
        
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, 
                               command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, 
                               command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scroll.set,
                            yscrollcommand=v_scroll.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Bindings del canvas
        self.setup_canvas_bindings()
        
    def setup_status_bar(self, parent):
        """Configura la barra de estado"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        # Información de estado
        info_label = ttk.Label(status_frame, textvariable=self.info_var)
        info_label.pack(side=tk.LEFT)
        
        # Contador de espacios
        spaces_info = ttk.Label(status_frame, 
                              text=f"Espacios: {len(self.spaces)}")
        spaces_info.pack(side=tk.RIGHT)
        self.spaces_info_label = spaces_info
        
    def setup_canvas_bindings(self):
        """Configura los eventos del canvas"""
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        
    def update_display(self):
        """Actualiza la visualización"""
        # Crear imagen con espacios dibujados
        display_frame = self.frame.copy()
        self.draw_spaces_on_frame(display_frame)
        
        # Convertir a formato Tkinter
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        
        # Crear PhotoImage
        from PIL import Image, ImageTk
        image = Image.fromarray(display_frame)
        self.photo = ImageTk.PhotoImage(image)
        
        # Configurar canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Actualizar contador
        self.spaces_info_label.configure(text=f"Espacios: {len(self.spaces)}")
        
    def draw_spaces_on_frame(self, frame):
        """Dibuja espacios en el frame"""
        for i, space in enumerate(self.spaces):
            # Color basado en selección
            if space == self.selected_space:
                color = (255, 255, 0)  # Amarillo para seleccionado
                thickness = 3
            else:
                color = (0, 255, 0)  # Verde normal
                thickness = 2
            
            # Dibujar rectángulo
            cv2.rectangle(frame, (space.x, space.y),
                         (space.x + space.width, space.y + space.height),
                         color, thickness)
            
            # Dibujar ID
            space_id = space.id or f"S{i:03d}"
            cv2.putText(frame, space_id, (space.x, space.y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Dibujar rectángulo en proceso de creación
        if self.is_drawing and self.drawing_start and self.drawing_current:
            cv2.rectangle(frame, self.drawing_start, self.drawing_current,
                         (255, 0, 0), 2)  # Rojo para el dibujo temporal
    
    def on_mode_change(self):
        """Maneja cambio de modo"""
        self.current_mode = self.mode_var.get()
        self.selected_space = None
        
        # Actualizar cursor
        cursors = {
            "select": "arrow",
            "draw": "crosshair", 
            "move": "fleur",
            "resize": "sizing",
            "delete": "pirate"
        }
        self.canvas.configure(cursor=cursors.get(self.current_mode, "arrow"))
        
        # Actualizar info
        mode_info = {
            "select": "Clic para seleccionar espacios",
            "draw": "Arrastra para dibujar nuevos espacios",
            "move": "Selecciona y arrastra para mover espacios",
            "resize": "Selecciona y arrastra esquinas para redimensionar",
            "delete": "Clic para eliminar espacios"
        }
        self.info_var.set(mode_info.get(self.current_mode, ""))
        
        self.update_display()
    
    def on_canvas_click(self, event):
        """Maneja clicks en el canvas"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.current_mode == "select":
            self.handle_select_click(int(x), int(y))
        elif self.current_mode == "draw":
            self.handle_draw_start(int(x), int(y))
        elif self.current_mode == "move":
            self.handle_move_click(int(x), int(y))
        elif self.current_mode == "resize":
            self.handle_resize_click(int(x), int(y))
        elif self.current_mode == "delete":
            self.handle_delete_click(int(x), int(y))
    
    def on_canvas_drag(self, event):
        """Maneja arrastre en el canvas"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        if self.current_mode == "draw" and self.is_drawing:
            self.handle_draw_drag(int(x), int(y))
        elif self.current_mode == "move" and self.selected_space:
            self.handle_move_drag(int(x), int(y))
    
    def on_canvas_release(self, event):
        """Maneja liberación del mouse"""
        if self.current_mode == "draw" and self.is_drawing:
            self.handle_draw_end()
    
    def on_canvas_motion(self, event):
        """Maneja movimiento del mouse"""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.info_var.set(f"Posición: ({int(x)}, {int(y)})")
    
    def on_canvas_right_click(self, event):
        """Maneja click derecho"""
        # Menú contextual aquí si es necesario
        pass
    
    def handle_select_click(self, x, y):
        """Maneja selección de espacios"""
        selected = None
        for space in self.spaces:
            if space.contains_point(x, y):
                selected = space
                break
        
        self.selected_space = selected
        if selected:
            self.info_var.set(f"Seleccionado: {selected.id or 'Sin ID'}")
        else:
            self.info_var.set("Ningún espacio seleccionado")
        
        self.update_display()
    
    def handle_draw_start(self, x, y):
        """Inicia dibujo de nuevo espacio"""
        self.drawing_start = (x, y)
        self.drawing_current = (x, y)
        self.is_drawing = True
    
    def handle_draw_drag(self, x, y):
        """Continúa dibujo de espacio"""
        self.drawing_current = (x, y)
        self.update_display()
    
    def handle_draw_end(self):
        """Finaliza dibujo de espacio"""
        if self.drawing_start and self.drawing_current:
            x1, y1 = self.drawing_start
            x2, y2 = self.drawing_current
            
            # Calcular rectángulo
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            # Validar tamaño mínimo
            if w > 10 and h > 10:
                space_id = f"NEW_{len(self.spaces):03d}"
                new_space = ParkingSpace(x, y, w, h, id=space_id)
                self.spaces.append(new_space)
                self.info_var.set(f"Espacio creado: {space_id}")
            
        self.is_drawing = False
        self.drawing_start = None
        self.drawing_current = None
        self.update_display()
    
    def handle_move_click(self, x, y):
        """Maneja click para mover"""
        self.handle_select_click(x, y)
    
    def handle_move_drag(self, x, y):
        """Maneja arrastre para mover"""
        if self.selected_space and self.drawing_start:
            dx = x - self.drawing_start[0]
            dy = y - self.drawing_start[1]
            
            self.selected_space.x += dx
            self.selected_space.y += dy
            
            self.drawing_start = (x, y)
            self.update_display()
    
    def handle_resize_click(self, x, y):
        """Maneja click para redimensionar"""
        self.handle_select_click(x, y)
        if self.selected_space:
            self.drawing_start = (x, y)
    
    def handle_delete_click(self, x, y):
        """Maneja click para eliminar"""
        to_remove = None
        for space in self.spaces:
            if space.contains_point(x, y):
                to_remove = space
                break
        
        if to_remove:
            self.spaces.remove(to_remove)
            self.info_var.set(f"Espacio eliminado")
            self.update_display()
    
    def auto_detect(self):
        """Detección automática de espacios"""
        from .detector import SmartDetector
        detector = SmartDetector()
        detected_spaces = detector.detect_spaces_combined(self.frame)
        
        if detected_spaces:
            # Agregar espacios detectados
            for space in detected_spaces:
                space.id = f"AUTO_{len(self.spaces):03d}"
                self.spaces.append(space)
            
            self.info_var.set(f"Detectados {len(detected_spaces)} espacios")
            self.update_display()
        else:
            messagebox.showinfo("Info", "No se detectaron espacios automáticamente")
    
    def clear_all(self):
        """Limpia todos los espacios"""
        if messagebox.askyesno("Confirmar", "¿Eliminar todos los espacios?"):
            self.spaces.clear()
            self.selected_space = None
            self.info_var.set("Todos los espacios eliminados")
            self.update_display()
    
    def apply_changes(self):
        """Aplica cambios y cierra"""
        if self.callback:
            self.callback(self.spaces)
        self.window.destroy()
    
    def cancel_changes(self):
        """Cancela cambios y cierra"""
        self.window.destroy()
    
    def on_close(self):
        """Maneja cierre de ventana"""
        if messagebox.askyesno("Confirmar", "¿Descartar cambios?"):
            self.window.destroy()
