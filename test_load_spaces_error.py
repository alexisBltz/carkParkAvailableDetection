#!/usr/bin/env python3
"""
Test específico para el error al cargar espacios y regresar al panel principal
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
import cv2
import numpy as np
from src.modern_gui import ModernCarParkGUI

def create_test_image():
    """Crear una imagen de prueba simulando un estacionamiento"""
    # Crear imagen de 800x600 con fondo gris
    img = np.full((600, 800, 3), 120, dtype=np.uint8)
    
    # Dibujar algunas líneas para simular espacios de estacionamiento
    for i in range(0, 800, 100):
        cv2.line(img, (i, 100), (i, 500), (255, 255, 255), 2)
    
    for i in range(100, 500, 80):
        cv2.line(img, (0, i), (800, i), (255, 255, 255), 2)
    
    # Agregar texto
    cv2.putText(img, "Test Parking Lot", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return img

def test_load_spaces_and_return():
    """Prueba específica del problema: cargar espacios y regresar al panel principal"""
    
    print("🧪 Iniciando test: Cargar espacios y regresar al panel principal")
    
    root = tk.Tk()
    app = ModernCarParkGUI(root)
    
    # Crear imagen de prueba
    test_image = create_test_image()
    app.current_frame = test_image
    
    def simulate_workflow():
        """Simular el workflow problemático"""
        try:
            print("📹 1. Simulando carga de imagen...")
            # Simular carga de imagen
            app.current_frame = test_image
            app.update_video_display()
            
            # Esperar un poco
            root.after(1000, switch_to_editor)
            
        except Exception as e:
            print(f"❌ Error en paso 1: {e}")
            import traceback
            traceback.print_exc()
    
    def switch_to_editor():
        """Cambiar al editor"""
        try:
            print("✏️ 2. Cambiando al editor de espacios...")
            # Cambiar a la pestaña del editor (índice 1)
            app.main_notebook.select(1)
            
            # Esperar un poco y simular carga de espacios
            root.after(1000, simulate_load_spaces)
            
        except Exception as e:
            print(f"❌ Error en paso 2: {e}")
            import traceback
            traceback.print_exc()
    
    def simulate_load_spaces():
        """Simular carga de espacios"""
        try:
            print("📂 3. Simulando carga de espacios...")
            # Crear espacios de prueba
            from src.models import ParkingSpace
            test_spaces = [
                ParkingSpace(id="1", x=50, y=150, width=90, height=70),
                ParkingSpace(id="2", x=150, y=150, width=90, height=70),
                ParkingSpace(id="3", x=250, y=150, width=90, height=70),
                ParkingSpace(id="4", x=350, y=150, width=90, height=70),
            ]
            
            app.spaces = test_spaces
            print(f"✅ Cargados {len(test_spaces)} espacios de prueba")
            
            # Forzar actualización
            app.force_update_all_displays()
            
            # Esperar y regresar al panel principal
            root.after(1500, return_to_main)
            
        except Exception as e:
            print(f"❌ Error en paso 3: {e}")
            import traceback
            traceback.print_exc()
    
    def return_to_main():
        """Regresar al panel principal (aquí ocurría el error)"""
        try:
            print("🏠 4. Regresando al panel principal...")
            # Cambiar a la pestaña principal (índice 0)
            app.main_notebook.select(0)
            
            print("✅ Cambio completado - verificando visualización...")
            
            # Esperar un poco para que se actualice
            root.after(500, final_check)
            
        except Exception as e:
            print(f"❌ Error en paso 4 (crítico): {e}")
            import traceback
            traceback.print_exc()
    
    def final_check():
        """Verificación final"""
        try:
            print("🔍 5. Verificación final...")
            
            # Verificar que la imagen se muestra correctamente
            if app.current_frame is not None:
                print("✅ Frame disponible")
            else:
                print("❌ No hay frame")
            
            # Verificar que los espacios están cargados
            if app.spaces:
                print(f"✅ {len(app.spaces)} espacios cargados")
            else:
                print("❌ No hay espacios")
            
            # Intentar actualización manual
            app.safe_update_video_display()
            print("✅ Actualización manual completada")
            
            print("🎉 Test completado exitosamente!")
            
        except Exception as e:
            print(f"❌ Error en verificación final: {e}")
            import traceback
            traceback.print_exc()
    
    # Comenzar el test después de que la interfaz esté lista
    root.after(500, simulate_workflow)
    
    # Configurar cierre automático después de 10 segundos
    root.after(10000, lambda: root.quit())
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Test interrumpido por el usuario")
    except Exception as e:
        print(f"Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load_spaces_and_return()
