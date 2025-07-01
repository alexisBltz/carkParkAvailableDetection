#!/usr/bin/env python3
"""
CarPark Project - Interfaz Simple con Selector de Analizador
Permite elegir entre el analizador simple y el working
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import cv2
import numpy as np
import pickle
from PIL import Image, ImageTk
from typing import List, Optional

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Verificar dependencias
def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    missing = []
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        from PIL import Image
    except ImportError:
        missing.append("pillow")
    
    if missing:
        print("❌ Dependencias faltantes:")
        for dep in missing:
            print(f"   - {dep}")
        print("\n📦 Instala las dependencias con:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

class SimpleCarParkGUI:
    """Interfaz simple para seleccionar y usar los analizadores"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🚗 CarPark - Analizador Simple")
        self.root.geometry("1200x800")
        
        # Variables
        self.current_frame = None
        self.spaces = []
        self.analysis_results = []
        self.analyzer_type = tk.StringVar(value="simple")
        
        # Importar analizadores
        try:
            from src.simple_analyzer import SimpleOccupancyAnalyzer
            from src.working_analyzer import WorkingOccupancyAnalyzer
            from src.models import ParkingSpace
            
            self.simple_analyzer = SimpleOccupancyAnalyzer()
            self.working_analyzer = WorkingOccupancyAnalyzer()
            self.ParkingSpace = ParkingSpace
            
        except ImportError as e:
            messagebox.showerror("Error", f"No se pudieron importar los analizadores: {e}")
            return
        
        self.setup_ui()
        self.load_spaces()
    
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de controles
        control_frame = ttk.LabelFrame(main_frame, text="🎛️ Controles", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Selector de analizador
        ttk.Label(control_frame, text="Tipo de Analizador:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        analyzer_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.analyzer_type,
            values=["simple", "working"],
            state="readonly",
            width=15
        )
        analyzer_combo.grid(row=0, column=1, padx=(0, 20))
        analyzer_combo.bind('<<ComboboxSelected>>', self.on_analyzer_change)
        
        # Botón cargar imagen
        ttk.Button(control_frame, text="📁 Cargar Imagen", command=self.load_image).grid(row=0, column=2, padx=(0, 10))
        
        # Botón cargar video
        ttk.Button(control_frame, text="🎥 Cargar Video", command=self.load_video).grid(row=0, column=3, padx=(0, 10))
        
        # Botón analizar
        ttk.Button(control_frame, text="🔍 Analizar", command=self.analyze_current).grid(row=0, column=4, padx=(0, 10))
        
        # Frame para imagen y resultados
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de imagen
        image_frame = ttk.LabelFrame(content_frame, text="📺 Vista", padding=5)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.image_label = ttk.Label(image_frame, text="Carga una imagen o video")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(content_frame, text="📊 Resultados", padding=5)
        results_frame.pack(side=tk.RIGHT, fill=tk.Y, ipadx=200)
        
        # Métricas
        self.total_var = tk.StringVar(value="0")
        self.occupied_var = tk.StringVar(value="0")
        self.free_var = tk.StringVar(value="0")
        self.percent_var = tk.StringVar(value="0.0%")
        
        ttk.Label(results_frame, text="Total de espacios:").pack(anchor=tk.W)
        ttk.Label(results_frame, textvariable=self.total_var, font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(results_frame, text="Espacios ocupados:").pack(anchor=tk.W)
        ttk.Label(results_frame, textvariable=self.occupied_var, font=("Arial", 14, "bold"), foreground="red").pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(results_frame, text="Espacios libres:").pack(anchor=tk.W)
        ttk.Label(results_frame, textvariable=self.free_var, font=("Arial", 14, "bold"), foreground="green").pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(results_frame, text="% Ocupación:").pack(anchor=tk.W)
        ttk.Label(results_frame, textvariable=self.percent_var, font=("Arial", 14, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # Info del analizador
        info_frame = ttk.LabelFrame(results_frame, text="ℹ️ Info del Analizador", padding=5)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame de estado
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Actualizar info inicial
        self.update_info()
    
    def on_analyzer_change(self, event=None):
        """Callback cuando cambia el analizador"""
        self.update_info()
        if self.current_frame is not None:
            self.analyze_current()
    
    def load_spaces(self):
        """Cargar espacios desde CarParkPos"""
        try:
            with open('assets/CarParkPos', 'rb') as f:
                pos_list = pickle.load(f)
            
            self.spaces = []
            width, height = 107, 48
            
            for i, (x, y) in enumerate(pos_list):
                space = self.ParkingSpace(
                    id=f"space_{i}",
                    x=x, y=y,
                    width=width, height=height
                )
                self.spaces.append(space)
            
            self.status_var.set(f"✅ Cargados {len(self.spaces)} espacios")
            
        except Exception as e:
            self.status_var.set(f"⚠️ Error cargando espacios: {e}")
            messagebox.showwarning("Advertencia", f"No se pudieron cargar los espacios: {e}")
    
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
        """Reproducir video con análisis en tiempo real"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            messagebox.showerror("Error", "No se pudo abrir el video")
            return
        
        self.status_var.set("🎥 Reproduciendo video... Cierra la ventana para parar")
        
        def update_frame():
            ret, frame = cap.read()
            
            if not ret:
                # Reiniciar video al final
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            
            if ret:
                self.current_frame = frame
                
                # Analizar frame actual
                if self.spaces:
                    self.analyze_frame_silent(frame)
                
                # Mostrar frame con análisis
                self.display_frame_with_analysis(frame)
                
                # Programar siguiente frame (más lento para mejor visualización)
                self.root.after(100, update_frame)  # 10 FPS
            else:
                cap.release()
                self.status_var.set("✅ Video finalizado")
        
        update_frame()
    
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
            messagebox.showerror("Error", f"Error en el análisis: {e}")
    
    def analyze_frame_silent(self, frame):
        """Analizar frame sin mostrar errores"""
        try:
            analyzer_type = self.analyzer_type.get()
            
            if analyzer_type == "simple":
                self.analysis_results = self.simple_analyzer.analyze_spaces(frame, self.spaces)
            else:  # working
                self.analysis_results = self.working_analyzer.analyze_spaces(frame, self.spaces)
            
            # Actualizar métricas
            total = len(self.analysis_results)
            occupied = sum(1 for r in self.analysis_results if r.is_occupied)
            free = total - occupied
            percent = (occupied / total * 100) if total > 0 else 0
            
            self.total_var.set(str(total))
            self.occupied_var.set(str(occupied))
            self.free_var.set(str(free))
            self.percent_var.set(f"{percent:.1f}%")
            
            # Actualizar status
            self.status_var.set(f"✅ Análisis completado - {analyzer_type} | Ocupados: {occupied}/{total}")
            
        except Exception as e:
            self.status_var.set(f"❌ Error en análisis: {e}")
    
    def display_frame(self, frame):
        """Mostrar frame en la interfaz"""
        try:
            # Redimensionar para la interfaz
            height, width = frame.shape[:2]
            max_width, max_height = 600, 400
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Convertir para tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Mantener referencia
            
        except Exception as e:
            self.status_var.set(f"❌ Error mostrando imagen: {e}")
    
    def display_frame_with_analysis(self, frame):
        """Mostrar frame con resultados del análisis"""
        try:
            display_frame = frame.copy()
            
            # Dibujar espacios
            for i, (space, result) in enumerate(zip(self.spaces, self.analysis_results)):
                color = (0, 0, 255) if result.is_occupied else (0, 255, 0)  # Rojo/Verde
                thickness = 3 if result.is_occupied else 2
                
                cv2.rectangle(display_frame, 
                             (space.x, space.y), 
                             (space.x + space.width, space.y + space.height), 
                             color, thickness)
                
                # Número del espacio
                cv2.putText(display_frame, str(i), 
                           (space.x + 5, space.y + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Estadísticas en la imagen
            total = len(self.analysis_results)
            occupied = sum(1 for r in self.analysis_results if r.is_occupied)
            free = total - occupied
            
            stats_text = f"Libres: {free}/{total} | Analizador: {self.analyzer_type.get()}"
            cv2.putText(display_frame, stats_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            self.display_frame(display_frame)
            
        except Exception as e:
            self.display_frame(frame)  # Mostrar frame original si hay error
    
    def update_info(self):
        """Actualizar información del analizador"""
        analyzer_type = self.analyzer_type.get()
        
        if analyzer_type == "simple":
            info = f"""🔹 ANALIZADOR SIMPLE:
• Método: Threshold de intensidad promedio
• Umbral: {self.simple_analyzer.get_threshold():.3f}
• Lógica: Espacios oscuros = ocupados
• Velocidad: ⚡ Muy rápida
• Precisión: ✅ Buena en condiciones estables

📋 CONFIGURACIÓN:
• Intensidad < {self.simple_analyzer.get_threshold():.3f} = OCUPADO
• Intensidad >= {self.simple_analyzer.get_threshold():.3f} = LIBRE

💡 CONSEJOS:
• Ajusta el umbral si no detecta bien
• Funciona mejor con buena iluminación
• Ideal para análisis rápido"""
        else:
            info = f"""🔸 ANALIZADOR WORKING:
• Método: Conteo de píxeles (como main.py exitoso)
• Umbral: {self.working_analyzer.get_pixel_threshold()} píxeles blancos
• Preprocesamiento: Gaussian → Adaptive → Median → Dilate
• Lógica: Píxeles blancos >= umbral = ocupado

📋 CONFIGURACIÓN:
• Píxeles >= {self.working_analyzer.get_pixel_threshold()} = OCUPADO  
• Píxeles < {self.working_analyzer.get_pixel_threshold()} = LIBRE

✨ VENTAJAS:
• Replica exactamente el código que funciona
• Más robusto ante cambios de iluminación
• Preprocesamiento avanzado"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)

def main():
    """Función principal"""
    print("🚗 CarPark Project - Interfaz Simple con Selector")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        input("\nPresiona Enter para salir...")
        return
    
    try:
        # Crear aplicación
        root = tk.Tk()
        app = SimpleCarParkGUI(root)
        
        print("✅ Interfaz simple iniciada")
        print("🎯 Puedes elegir entre:")
        print("   • 'simple': Analizador por threshold de intensidad")
        print("   • 'working': Analizador que replica tu código exitoso")
        print("📍 Usa Ctrl+C para cerrar desde la terminal")
        
        # Ejecutar loop principal
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        messagebox.showerror("Error", f"Error de importación: {e}")
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        messagebox.showerror("Error", f"Error inesperado: {e}")
    
    finally:
        print("\n👋 Aplicación cerrada")

if __name__ == "__main__":
    main()
