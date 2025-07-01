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

class CarParkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CarPark Project - Profesional")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Estado
        self.img = None
        self.img_cv = None
        self.video_path = None
        self.cap = None
        self.posList = []
        self.rect_start = None
        self.rect_preview = None
        self.selected = None
        self.drawing = False
        self.moving = False
        self.move_offset = (0, 0)
        self.clipboard_rect = None
        self.resizing = False
        self.resize_corner = None
        self.analysis_result = []
        self.video_paused = True
        self.current_frame = None
        self.undo_stack = []
        self.redo_stack = []
        self.analysis_history = []
        self.is_analyzing = False
        self.analysis_mode = False  # Inicializar analysis_mode
        self.frame_count = 0
        
        # UI
        self.create_widgets()
        self.bind_shortcuts()
        self.update_canvas()
        
    def create_widgets(self):
        # Menú principal
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo proyecto", command=self.new_project)
        file_menu.add_command(label="Abrir imagen/video", command=self.load_image)
        file_menu.add_command(label="Usar cámara", command=self.use_camera)
        file_menu.add_separator()
        file_menu.add_command(label="Guardar posiciones", command=self.save_positions)
        file_menu.add_command(label="Cargar posiciones", command=self.load_positions)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar estadísticas", command=self.export_stats)
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Detección automática", command=self.auto_detect)
        tools_menu.add_command(label="Mostrar contornos", command=self.show_contours_preview)
        tools_menu.add_command(label="Limpiar espacios", command=self.clear_spaces)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Instrucciones", command=self.show_help)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
        # Panel lateral izquierdo
        left_panel = tk.Frame(self.root, bg="#e8e8e8", width=280)
        left_panel.pack(side="left", fill="y", padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Sección: Fuente
        source_frame = tk.LabelFrame(left_panel, text="Fuente de video", bg="#e8e8e8")
        source_frame.pack(fill='x', pady=5, padx=5)
        
        tk.Button(source_frame, text="📁 Cargar archivo", command=self.load_image, bg="#4CAF50", fg="white").pack(fill='x', pady=2, padx=5)
        tk.Button(source_frame, text="📷 Usar cámara", command=self.use_camera, bg="#2196F3", fg="white").pack(fill='x', pady=2, padx=5)
        
        # Controles de video
        video_frame = tk.LabelFrame(left_panel, text="Control de video", bg="#e8e8e8")
        video_frame.pack(fill='x', pady=5, padx=5)
        
        control_frame = tk.Frame(video_frame, bg="#e8e8e8")
        control_frame.pack(fill='x', pady=2)
        
        tk.Button(control_frame, text="⏸️", command=self.toggle_video, width=3).pack(side="left", padx=2)
        tk.Button(control_frame, text="📸", command=self.capture_frame, width=3).pack(side="left", padx=2)
        tk.Button(control_frame, text="⏮️", command=self.prev_frame, width=3).pack(side="left", padx=2)
        tk.Button(control_frame, text="⏭️", command=self.next_frame, width=3).pack(side="left", padx=2)
        
        # Sección: Espacios
        spaces_frame = tk.LabelFrame(left_panel, text="Definir espacios", bg="#e8e8e8")
        spaces_frame.pack(fill='x', pady=5, padx=5)
        
        tk.Button(spaces_frame, text="🤖 Detección automática", command=self.auto_detect, bg="#FF9800", fg="white").pack(fill='x', pady=2, padx=5)
        tk.Button(spaces_frame, text="✏️ Definir manualmente", command=self.set_draw_mode, bg="#9C27B0", fg="white").pack(fill='x', pady=2, padx=5)
        tk.Button(spaces_frame, text="👁️ Ver contornos", command=self.show_contours_preview, bg="#607D8B", fg="white").pack(fill='x', pady=2, padx=5)
        
        # Sección: Edición
        edit_frame = tk.LabelFrame(left_panel, text="Edición", bg="#e8e8e8")
        edit_frame.pack(fill='x', pady=5, padx=5)
        
        edit_row1 = tk.Frame(edit_frame, bg="#e8e8e8")
        edit_row1.pack(fill='x', pady=2)
        tk.Button(edit_row1, text="📋", command=self.copy_selected, width=4).pack(side="left", padx=2)
        tk.Button(edit_row1, text="📌", command=self.paste_clipboard, width=4).pack(side="left", padx=2)
        tk.Button(edit_row1, text="🗑️", command=self.delete_selected, width=4).pack(side="left", padx=2)
        
        edit_row2 = tk.Frame(edit_frame, bg="#e8e8e8")
        edit_row2.pack(fill='x', pady=2)
        tk.Button(edit_row2, text="↶", command=self.undo, width=4).pack(side="left", padx=2)
        tk.Button(edit_row2, text="↷", command=self.redo, width=4).pack(side="left", padx=2)
        tk.Button(edit_row2, text="🧹", command=self.clear_spaces, width=4).pack(side="left", padx=2)
        
        # Sección: Análisis
        analysis_frame = tk.LabelFrame(left_panel, text="Análisis", bg="#e8e8e8")
        analysis_frame.pack(fill='x', pady=5, padx=5)
        
        tk.Button(analysis_frame, text="▶️ Iniciar análisis", command=self.start_analysis, bg="#4CAF50", fg="white").pack(fill='x', pady=2, padx=5)
        tk.Button(analysis_frame, text="⏹️ Detener análisis", command=self.stop_analysis, bg="#f44336", fg="white").pack(fill='x', pady=2, padx=5)
        
        # Estadísticas en tiempo real
        self.stats_frame = tk.LabelFrame(left_panel, text="Estadísticas", bg="#e8e8e8")
        self.stats_frame.pack(fill='x', pady=5, padx=5)
        
        self.libres_label = tk.Label(self.stats_frame, text="Libres: 0", bg="#e8e8e8", fg="green", font=("Arial", 12, "bold"))
        self.libres_label.pack()
        
        self.ocupados_label = tk.Label(self.stats_frame, text="Ocupados: 0", bg="#e8e8e8", fg="red", font=("Arial", 12, "bold"))
        self.ocupados_label.pack()
        
        self.total_label = tk.Label(self.stats_frame, text="Total: 0", bg="#e8e8e8", font=("Arial", 10))
        self.total_label.pack()
        
        # Sección: Archivos
        files_frame = tk.LabelFrame(left_panel, text="Archivos", bg="#e8e8e8")
        files_frame.pack(fill='x', pady=5, padx=5)
        
        tk.Button(files_frame, text="💾 Guardar posiciones", command=self.save_positions, bg="#795548", fg="white").pack(fill='x', pady=2, padx=5)
        tk.Button(files_frame, text="📂 Cargar posiciones", command=self.load_positions, bg="#607D8B", fg="white").pack(fill='x', pady=2, padx=5)
        tk.Button(files_frame, text="📊 Exportar estadísticas", command=self.export_stats, bg="#FF5722", fg="white").pack(fill='x', pady=2, padx=5)
        
        # Status bar en la parte inferior del panel
        self.status = tk.Label(left_panel, text="Listo. Carga una imagen/video para comenzar.", bg="#e8e8e8", fg="#333", wraplength=260, justify="left", font=("Arial", 9))
        self.status.pack(fill='x', pady=10, padx=5)
        
        # Canvas principal
        self.canvas = tk.Canvas(self.root, width=900, height=700, bg="#222")
        self.canvas.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)
        
    def bind_shortcuts(self):
        self.root.bind('<Control-c>', self.copy_selected)
        self.root.bind('<Control-C>', self.copy_selected)
        self.root.bind('<Control-v>', self.paste_clipboard)
        self.root.bind('<Control-V>', self.paste_clipboard)
        self.root.bind('<Delete>', self.delete_selected)
        self.root.bind('<Control-z>', self.undo)
        self.root.bind('<Control-Z>', self.undo)
        self.root.bind('<Control-y>', self.redo)
        self.root.bind('<Control-Y>', self.redo)
        self.root.bind('<space>', self.toggle_video)
        
    def new_project(self):
        if messagebox.askyesno("Nuevo proyecto", "¿Estás seguro? Se perderán los cambios no guardados."):
            self.reset_all()
            
    def prev_frame(self):
        if self.cap and self.video_path:
            current_pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, current_pos - 1))
            ret, frame = self.cap.read()
            if ret:
                self.img_cv = frame.copy()
                self.current_frame = frame.copy()
                
    def next_frame(self):
        if self.cap and self.video_path:
            ret, frame = self.cap.read()
            if ret:
                self.img_cv = frame.copy()
                self.current_frame = frame.copy()
                
    def clear_spaces(self):
        if self.posList and messagebox.askyesno("Limpiar espacios", "¿Eliminar todos los espacios definidos?"):
            self.undo_stack.append(self.posList.copy())
            self.posList = []
            self.selected = None
            self.set_status("Todos los espacios eliminados")
            
    def undo(self, event=None):
        if self.undo_stack:
            self.redo_stack.append(self.posList.copy())
            self.posList = self.undo_stack.pop()
            self.selected = None
            self.set_status("Deshacer")
            
    def redo(self, event=None):
        if self.redo_stack:
            self.undo_stack.append(self.posList.copy())
            self.posList = self.redo_stack.pop()
            self.selected = None
            self.set_status("Rehacer")
            
    def export_stats(self):
        if not self.analysis_history:
            messagebox.showinfo("Sin datos", "No hay estadísticas para exportar.")
            return
            
        save_path = filedialog.asksaveasfilename(
            title="Exportar estadísticas",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*")]
        )
        
        if save_path:
            with open(save_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Libres", "Ocupados", "Total", "Porcentaje_Ocupacion"])
                for entry in self.analysis_history:
                    writer.writerow(entry)
            messagebox.showinfo("Éxito", f"Estadísticas exportadas a {save_path}")
            
    def show_about(self):
        messagebox.showinfo(
            "Acerca de",
            "CarPark Project v2.0\n\n"
            "Sistema profesional para detección y análisis\n"
            "de espacios de estacionamiento.\n\n"
            "Desarrollado con Python, OpenCV y Tkinter."
        )
        
    def stop_analysis(self):
        self.is_analyzing = False
        self.set_status("Análisis detenido")
        
    def update_stats_display(self):
        """Actualiza las estadísticas mostradas en el panel"""
        if self.analysis_result:
            libres = self.analysis_result.count(False)
            ocupados = self.analysis_result.count(True)
            total = len(self.analysis_result)
            porcentaje_ocupado = (ocupados / total * 100) if total > 0 else 0
            
            # Actualizar etiquetas con colores apropiados
            self.libres_label.config(text=f"🟢 Libres: {libres}")
            self.ocupados_label.config(text=f"🔴 Ocupados: {ocupados}")
            self.total_label.config(text=f"📊 Total: {total} ({porcentaje_ocupado:.1f}% ocupado)")
            
            # Guardar en historial con timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.analysis_history.append([timestamp, libres, ocupados, total, f"{porcentaje_ocupado:.1f}%"])
            
            # Limitar historial a las últimas 50 entradas
            if len(self.analysis_history) > 50:
                self.analysis_history = self.analysis_history[-50:]
                
        else:
            # Sin resultados de análisis
            total_spaces = len(self.posList)
            self.libres_label.config(text="🟢 Libres: -")
            self.ocupados_label.config(text="🔴 Ocupados: -")
            self.total_label.config(text=f"📊 Espacios definidos: {total_spaces}")
    
    def reset_stats_display(self):
        """Reinicia la visualización de estadísticas"""
        self.analysis_result = []
        self.analysis_mode = False
        self.update_stats_display()
            
    def update_canvas(self):
        # Video/cámara en tiempo real (SOLO si NO estamos en modo análisis)
        if self.cap and not self.video_paused and not self.analysis_mode:
            ret, frame = self.cap.read()
            if ret:
                self.img_cv = frame.copy()
                self.current_frame = frame.copy()
        
        if self.img_cv is not None:
            img_disp = self.img_cv.copy()
            
            # Debug: Verificar si hay espacios para dibujar
            if self.posList:
                print(f"DEBUG: Dibujando {len(self.posList)} espacios, analysis_result: {len(self.analysis_result) if self.analysis_result else 0}")
            
            # Dibujar espacios de estacionamiento
            for idx, pos in enumerate(self.posList):
                # Manejar diferentes formatos de datos
                if len(pos) == 4:
                    x, y, w, h = pos
                elif len(pos) == 2:
                    # Formato (x, y) - asumir tamaño por defecto
                    x, y = pos
                    w, h = 80, 40  # Tamaño por defecto
                    print(f"DEBUG: Espacio {idx+1} convertido de (x,y) a (x,y,w,h): ({x},{y},{w},{h})")
                else:
                    print(f"DEBUG: Formato de posición no válido en índice {idx}: {pos}")
                    continue
                # Determinar color del rectángulo
                if self.analysis_result and idx < len(self.analysis_result):
                    # Si hay análisis, usar colores de ocupación
                    ocupado = self.analysis_result[idx]
                    color = (0, 0, 255) if ocupado else (0, 255, 0)  # Rojo=ocupado, Verde=libre
                    thickness = 3
                    print(f"DEBUG: Espacio {idx+1} - Análisis: {'Ocupado' if ocupado else 'Libre'}")
                else:
                    # Sin análisis, usar colores de edición
                    color = (0, 255, 255) if idx != self.selected else (255, 0, 0)  # Amarillo normal, Rojo seleccionado
                    thickness = 2
                    print(f"DEBUG: Espacio {idx+1} - Sin análisis, color edición")
                
                # Dibujar rectángulo con bordes más visibles
                cv2.rectangle(img_disp, (x, y), (x + w, y + h), color, thickness)
                
                # Agregar número del espacio con fondo más visible
                text = str(idx + 1)
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                text_x = x + (w - text_size[0]) // 2
                text_y = y + (h + text_size[1]) // 2
                
                # Fondo negro para el texto para mejor contraste
                cv2.rectangle(img_disp, (text_x - 3, text_y - text_size[1] - 3), 
                             (text_x + text_size[0] + 3, text_y + 3), (0, 0, 0), -1)
                cv2.putText(img_disp, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Esquinas para redimensionar (solo en modo edición)
                if idx == self.selected and not self.analysis_mode:
                    for cx, cy in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
                        cv2.rectangle(img_disp, (cx-5, cy-5), (cx+5, cy+5), (0,255,0), -1)
            
            # Mostrar indicador de modo análisis
            if self.analysis_mode:
                # Agregar texto de modo análisis en la esquina superior
                analysis_text = "MODO ANÁLISIS - Frame capturado"
                text_size = cv2.getTextSize(analysis_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
                # Fondo semi-transparente
                overlay = img_disp.copy()
                cv2.rectangle(overlay, (10, 10), (text_size[0] + 30, text_size[1] + 30), (0, 0, 255), -1)
                cv2.addWeighted(overlay, 0.7, img_disp, 0.3, 0, img_disp)
                cv2.putText(img_disp, analysis_text, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            if self.rect_preview:
                x, y, w, h = self.rect_preview
                cv2.rectangle(img_disp, (x, y), (x + w, y + h), (0, 255, 0), 2)
            img_disp = cv2.cvtColor(img_disp, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_disp)
            img_tk = ImageTk.PhotoImage(img_pil.resize((800, 600)))
            self.canvas.img_tk = img_tk
            self.canvas.create_image(0, 0, anchor="nw", image=img_tk)
        self.root.after(30, self.update_canvas)
    def toggle_video(self):
        if self.cap:
            self.video_paused = not self.video_paused
            self.set_status("Video pausado" if self.video_paused else "Video/cámara en reproducción")
    def capture_frame(self):
        if self.img_cv is not None:
            self.video_paused = True
            self.set_status("Frame capturado para detección. Ahora puedes usar la detección automática.")
    def show_contours_preview(self):
        if self.img_cv is None:
            self.set_status("Carga una imagen/video/cámara primero.")
            return
        # Mostrar contornos detectados (sin filtrar)
        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 1)
        edges = cv2.Canny(blur, 50, 150)
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        preview = self.img_cv.copy()
        cv2.drawContours(preview, contours, -1, (0,255,0), 2)
        cv2.imshow("Contornos detectados (previsualización)", preview)
        self.set_status("Previsualización de contornos mostrada en ventana aparte.")
    def load_image(self):
        path = filedialog.askopenfilename(title="Selecciona imagen/video", filetypes=[("Archivos", "*.png;*.jpg;*.jpeg;*.bmp;*.mp4;*.avi")])
        if not path:
            return
        # Liberar video/cámara si estaba activo
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_paused = True
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.mp4', '.avi']:
            self.cap = cv2.VideoCapture(path)
            ret, frame = self.cap.read()
            if not ret:
                messagebox.showerror("Error", "No se pudo leer el video.")
                return
            self.img_cv = frame.copy()
            self.current_frame = frame.copy()
            self.video_path = path
        else:
            img = cv2.imread(path)
            if img is None:
                messagebox.showerror("Error", "No se pudo leer la imagen.")
                return
            self.img_cv = img.copy()
            self.current_frame = img.copy()
            self.video_path = path
        self.posList = []
        self.analysis_mode = False
        self.set_status("Imagen/video cargado. Puedes definir espacios.")
    def use_camera(self):
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return
        self.img_cv = frame.copy()
        self.analysis_mode = False
        self.set_status("Cámara activada. Puedes definir espacios.")
    def auto_detect(self):
        if self.img_cv is None:
            self.set_status("Primero carga una imagen/video/cámara.")
            return
        # Panel de parámetros
        param_win = tk.Toplevel(self.root)
        param_win.title("Parámetros de Detección Automática")
        tk.Label(param_win, text="Área mínima (px²):").grid(row=0, column=0)
        min_area_var = tk.IntVar(value=3500)
        tk.Entry(param_win, textvariable=min_area_var, width=8).grid(row=0, column=1)
        tk.Label(param_win, text="Área máxima (px²):").grid(row=1, column=0)
        max_area_var = tk.IntVar(value=7000)
        tk.Entry(param_win, textvariable=max_area_var, width=8).grid(row=1, column=1)
        tk.Label(param_win, text="Relación ancho/alto mínima:").grid(row=2, column=0)
        min_ratio_var = tk.DoubleVar(value=1.5)
        tk.Entry(param_win, textvariable=min_ratio_var, width=8).grid(row=2, column=1)
        tk.Label(param_win, text="Relación ancho/alto máxima:").grid(row=3, column=0)
        max_ratio_var = tk.DoubleVar(value=3.0)
        tk.Entry(param_win, textvariable=max_ratio_var, width=8).grid(row=3, column=1)
        tk.Label(param_win, text="Modo de detección:").grid(row=4, column=0)
        mode_var = tk.StringVar(value="avanzado")
        tk.Radiobutton(param_win, text="Avanzado", variable=mode_var, value="avanzado").grid(row=4, column=1, sticky='w')
        tk.Radiobutton(param_win, text="Simple", variable=mode_var, value="simple").grid(row=5, column=1, sticky='w')
        def aplicar():
            min_area = min_area_var.get()
            max_area = max_area_var.get()
            min_ratio = min_ratio_var.get()
            max_ratio = max_ratio_var.get()
            modo = mode_var.get()
            if modo == "avanzado":
                sugeridos = self.detectar_espacios(self.img_cv, min_area, max_area, min_ratio, max_ratio)
            else:
                sugeridos = self.detectar_espacios_simple(self.img_cv, min_area, max_area, min_ratio, max_ratio)
            self.posList = sugeridos
            self.analysis_mode = False
            self.set_status(f"Detección ({modo}): {len(sugeridos)} espacios sugeridos. Puedes editar.")
            param_win.destroy()
        tk.Button(param_win, text="Aplicar", command=aplicar).grid(row=6, column=0, columnspan=2, pady=8)
    def detectar_espacios(self, img, min_area=3500, max_area=7000, min_ratio=1.5, max_ratio=3.0):
        # Conversión y preprocesado
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 2)
        edges = cv2.Canny(blur, 40, 120)
        kernel = np.ones((7, 7), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        # Detección de líneas para sugerir alineación
        lines = cv2.HoughLinesP(dilated, 1, np.pi/180, threshold=80, minLineLength=60, maxLineGap=20)
        line_img = np.zeros_like(gray)
        if lines is not None:
            for l in lines:
                x1, y1, x2, y2 = l[0]
                cv2.line(line_img, (x1, y1), (x2, y2), 255, 2)
        # Combinar bordes y líneas
        combined = cv2.bitwise_or(dilated, line_img)
        # Buscar contornos
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        posibles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            ratio = w / h if h != 0 else 0
            if min_area < area < max_area and min_ratio < ratio < max_ratio:
                posibles.append((x, y, w, h))
        # Agrupar por filas usando la coordenada Y
        posibles.sort(key=lambda r: (round(r[1]/30), r[0]))
        # Ajustar tamaño promedio por fila
        filas = {}
        for x, y, w, h in posibles:
            fy = round(y/30)
            if fy not in filas:
                filas[fy] = []
            filas[fy].append((x, y, w, h))
        sugeridos = []
        for fila in filas.values():
            if len(fila) < 2:
                continue
            avg_w = int(np.median([w for x, y, w, h in fila]))
            avg_h = int(np.median([h for x, y, w, h in fila]))
            for x, y, w, h in fila:
                sugeridos.append((x, y, avg_w, avg_h))
        return sugeridos
    def detectar_espacios_simple(self, img, min_area=3500, max_area=7000, min_ratio=1.5, max_ratio=3.0):
        # Detección simple: solo contornos
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 1)
        edges = cv2.Canny(blur, 50, 150)
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        posibles = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            ratio = w / h if h != 0 else 0
            if min_area < area < max_area and min_ratio < ratio < max_ratio:
                posibles.append((x, y, w, h))
        posibles = sorted(posibles, key=lambda r: (r[1]//20, r[0]))
        return posibles
    def set_draw_mode(self):
        self.paste_mode = False
        self.set_status("Modo: dibujar espacio (clic y arrastra)")
    def on_mouse_down(self, event):
        if self.img_cv is None:
            return
        x, y = int(event.x * self.img_cv.shape[1] / 800), int(event.y * self.img_cv.shape[0] / 600)
        # Selección de cuadro
        for idx, pos in enumerate(self.posList):
            px, py, pw, ph = self.normalize_position(pos)
            if px <= x <= px+pw and py <= y <= py+ph:
                self.selected = idx
                # ¿Redimensionar?
                for corner, (cx, cy) in enumerate([(px, py), (px+pw, py), (px, py+ph), (px+pw, py+ph)]):
                    if abs(x-cx) < 8 and abs(y-cy) < 8:
                        self.resizing = True
                        self.resize_corner = corner
                        self.set_status("Redimensionando espacio")
                        return
                # ¿Mover?
                self.moving = True
                self.move_offset = (x - px, y - py)
                self.set_status("Moviendo espacio")
                return
        # Si no selecciona ninguno, inicia dibujo
        self.selected = None
        self.drawing = True
        self.rect_start = (x, y)
        self.rect_preview = None
    def on_mouse_drag(self, event):
        if self.img_cv is None:
            return
        x, y = int(event.x * self.img_cv.shape[1] / 800), int(event.y * self.img_cv.shape[0] / 600)
        if self.drawing and self.rect_start:
            x0, y0 = self.rect_start
            rx, ry = min(x0, x), min(y0, y)
            rw, rh = abs(x - x0), abs(y - y0)
            self.rect_preview = (rx, ry, rw, rh)
        elif self.moving and self.selected is not None:
            ox, oy, w, h = self.normalize_position(self.posList[self.selected])
            dx, dy = self.move_offset
            new_x, new_y = x - dx, y - dy
            self.posList[self.selected] = (new_x, new_y, w, h)
        elif self.resizing and self.selected is not None:
            x0, y0, w, h = self.normalize_position(self.posList[self.selected])
            if self.resize_corner == 0:  # top-left
                nx, ny = x, y
                nw, nh = (x0 + w) - nx, (y0 + h) - ny
                if nw > 5 and nh > 5:
                    self.posList[self.selected] = (nx, ny, nw, nh)
            elif self.resize_corner == 1:  # top-right
                ny = y
                nw, nh = x - x0, (y0 + h) - ny
                if nw > 5 and nh > 5:
                    self.posList[self.selected] = (x0, ny, nw, nh)
            elif self.resize_corner == 2:  # bottom-left
                nx = x
                nw, nh = (x0 + w) - nx, y - y0
                if nw > 5 and nh > 5:
                    self.posList[self.selected] = (nx, y0, nw, nh)
            elif self.resize_corner == 3:  # bottom-right
                nw, nh = x - x0, y - y0
                if nw > 5 and nh > 5:
                    self.posList[self.selected] = (x0, y0, nw, nh)
    def on_mouse_up(self, event):
        if self.img_cv is None:
            return
        if self.drawing and self.rect_preview:
            x, y, w, h = self.rect_preview
            if w > 5 and h > 5:
                self.posList.append((x, y, w, h))
            self.rect_preview = None
        self.drawing = False
        self.moving = False
        self.resizing = False
        self.resize_corner = None
    def on_right_click(self, event):
        # Eliminar el más cercano
        if self.img_cv is None or not self.posList:
            return
        x, y = int(event.x * self.img_cv.shape[1] / 800), int(event.y * self.img_cv.shape[0] / 600)
        dists = [abs(px-x)+abs(py-y) for px,py,_,_ in self.posList]
        if dists:
            idx = dists.index(min(dists))
            self.posList.pop(idx)
            self.selected = None
    def copy_selected(self, event=None):
        if self.selected is not None and 0 <= self.selected < len(self.posList):
            self.clipboard_rect = self.posList[self.selected]
            self.set_status("Espacio copiado (Ctrl+V para pegar)")
    def paste_clipboard(self, event=None):
        if self.clipboard_rect:
            x, y, w, h = self.clipboard_rect
            # Pega desplazado para que se vea
            self.posList.append((x+20, y+20, w, h))
            self.set_status("Espacio pegado")
    def delete_selected(self, event=None):
        if self.selected is not None and 0 <= self.selected < len(self.posList):
            self.posList.pop(self.selected)
            self.selected = None
            self.set_status("Espacio eliminado")
    def save_positions(self):
        if not self.posList:
            messagebox.showinfo("Sin datos", "No hay espacios para guardar.")
            return
        save_path = filedialog.asksaveasfilename(title="Guardar posiciones", defaultextension=".pkl", filetypes=[("Pickle", "*.pkl"), ("Todos", "*.*")])
        if save_path:
            with open(save_path, 'wb') as f:
                pickle.dump(self.posList, f)
            messagebox.showinfo("Éxito", f"Posiciones guardadas en {save_path}")
    def load_positions(self):
        path = filedialog.askopenfilename(title="Selecciona archivo de posiciones", filetypes=[("Pickle", "*.pkl"), ("Todos", "*.*")])
        if path:
            with open(path, 'rb') as f:
                self.posList = pickle.load(f)
            self.analysis_mode = False
            self.analysis_result = []  # Limpiar resultados de análisis anterior
            self.update_stats_display()  # Actualizar estadísticas
            self.set_status(f"Archivo de posiciones cargado. {len(self.posList)} espacios definidos.")
    def start_analysis(self):
        if self.img_cv is None or not self.posList:
            self.set_status("Carga una imagen/video y define espacios primero.")
            messagebox.showwarning("Datos insuficientes", 
                                 "Necesitas cargar una imagen/video y definir al menos un espacio de estacionamiento.")
            return
        
        # CAPTURAR FRAME ACTUAL Y PAUSAR VIDEO
        if self.cap and not self.video_paused:
            # Capturar el frame actual antes de pausar
            ret, current_frame = self.cap.read()
            if ret:
                self.img_cv = current_frame.copy()
            # Pausar el video automáticamente
            self.video_paused = True
            self.set_status("Video pausado automáticamente para análisis...")
        
        # Limpiar resultados anteriores
        self.analysis_result = []
        self.is_analyzing = True
        self.analysis_mode = True  # Activar modo análisis para visualización
        self.set_status("Análisis en curso...")
        
        # Hilo para análisis en segundo plano
        def analizar():
            try:
                img_gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
                
                for i, pos in enumerate(self.posList):
                    x, y, w, h = self.normalize_position(pos)
                    # Actualizar progreso
                    self.root.after(0, lambda i=i: self.set_status(f"Analizando espacio {i+1}/{len(self.posList)}..."))
                    
                    crop = img_gray[y:y+h, x:x+w]
                    if crop.size > 0:
                        mean = np.mean(crop)
                        ocupado = mean < 120  # Umbral configurable
                        self.analysis_result.append(ocupado)
                    else:
                        self.analysis_result.append(False)  # Espacio inválido = libre
                    
                    time.sleep(0.1)  # Simular tiempo de procesamiento
                
                # Actualizar interfaz en hilo principal
                self.root.after(0, self.finish_analysis)
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_analysis_error(str(e)))
        
        threading.Thread(target=analizar, daemon=True).start()
    
    def finish_analysis(self):
        """Finaliza el análisis y actualiza la interfaz"""
        self.is_analyzing = False
        # Mantener analysis_mode = True para seguir mostrando colores
        self.update_stats_display()
        
        # Mostrar resultados
        libres = self.analysis_result.count(False)
        ocupados = self.analysis_result.count(True)
        total = len(self.analysis_result)
        
        self.set_status(f"Análisis completado: {libres} libres, {ocupados} ocupados de {total} espacios - Usa 'Detener análisis' para volver al modo edición")
        
        # Mostrar notificación de éxito
        messagebox.showinfo("Análisis completado", 
                           f"Análisis finalizado exitosamente:\n\n"
                           f"🟢 Espacios libres: {libres}\n"
                           f"🔴 Espacios ocupados: {ocupados}\n"
                           f"📊 Total analizado: {total}\n\n"
                           f"Los resultados se muestran con colores en la imagen.\n"
                           f"Usa 'Detener análisis' para volver al modo edición.")
    
    def handle_analysis_error(self, error_msg):
        """Maneja errores durante el análisis"""
        self.is_analyzing = False
        self.analysis_mode = False
        self.set_status("Error en el análisis")
        messagebox.showerror("Error en análisis", 
                           f"Ocurrió un error durante el análisis:\n\n{error_msg}")
    
    def stop_analysis(self):
        """Detiene el análisis y regresa al modo normal"""
        if not self.analysis_mode and not self.is_analyzing:
            messagebox.showinfo("Sin análisis activo", "No hay ningún análisis en curso.")
            return
        
        # Detener análisis
        self.analysis_mode = False
        self.is_analyzing = False
        
        # Preguntar si quiere reanudar el video
        if self.cap and self.video_paused:
            resume_video = messagebox.askyesno(
                "Reanudar video", 
                "¿Quieres reanudar la reproducción del video?\n\n"
                "• SÍ: Continuar viendo el video en tiempo real\n"
                "• NO: Mantener la imagen actual pausada"
            )
            if resume_video:
                self.video_paused = False
                self.set_status("Video reanudado - Modo edición activado")
        
        # Mantener los resultados pero cambiar al modo edición
        if self.analysis_result:
            # Preguntar si quiere mantener los resultados
            keep_results = messagebox.askyesno(
                "Conservar resultados", 
                "¿Quieres mantener los resultados del análisis?\n\n"
                "• SÍ: Conservar estadísticas\n"
                "• NO: Limpiar resultados completamente"
            )
            
            if not keep_results:
                self.reset_stats_display()
                self.set_status("Análisis limpiado - Modo edición activado")
            else:
                self.set_status("Análisis detenido - Resultados conservados - Modo edición activado")
        else:
            self.set_status("Análisis detenido - Modo edición activado")
    def reset_all(self):
        """Reinicia todo el estado de la aplicación"""
        # Liberar recursos de video/cámara
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Reiniciar todas las variables de estado
        self.img_cv = None
        self.img = None
        self.video_path = None
        self.posList = []
        self.rect_start = None
        self.rect_preview = None
        self.selected = None
        self.drawing = False
        self.moving = False
        self.resizing = False
        self.last_rect = None
        self.paste_mode = False
        self.clipboard_rect = None
        self.video_paused = True
        self.current_frame = None
        self.undo_stack = []
        self.redo_stack = []
        self.analysis_history = []
        self.frame_count = 0
        
        # Reiniciar análisis
        self.reset_stats_display()
        
        # Limpiar canvas
        self.canvas.delete("all")
        
        self.set_status("Reiniciado. Carga una imagen/video para comenzar.")
        
        # Mostrar confirmación
        messagebox.showinfo("Proyecto reiniciado", "El proyecto ha sido reiniciado completamente.")
    def set_status(self, msg):
        self.status.config(text=msg)
    def show_help(self):
        messagebox.showinfo(
            "Ayuda",
            "- Cargar imagen/video/cámara\n"
            "- Definir espacios manualmente (clic y arrastra) o usar detección automática\n"
            "- Selecciona, mueve, redimensiona, copia (Ctrl+C), pega (Ctrl+V), elimina (Supr)\n"
            "- Guarda/carga posiciones\n"
            "- Inicia análisis para ver libres/ocupados\n"
            "- Reinicia para empezar de nuevo\n"
        )
    def normalize_position(self, pos):
        """Normaliza una posición a formato (x, y, w, h)"""
        if len(pos) == 4:
            return pos
        elif len(pos) == 2:
            x, y = pos
            return (x, y, 80, 40)  # Tamaño por defecto
        else:
            raise ValueError(f"Formato de posición no válido: {pos}")
    
    def get_normalized_positions(self):
        """Retorna todas las posiciones normalizadas a formato (x, y, w, h)"""
        return [self.normalize_position(pos) for pos in self.posList]

def main():
    root = tk.Tk()
    app = CarParkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
