#!/usr/bin/env python3
"""
Test para verificar las correcciones de la GUI moderna
"""

import tkinter as tk
import sys
import os
import time

# Configurar path para las importaciones
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, current_dir)
sys.path.insert(0, src_path)

# Importar los módulos necesarios
try:
    from src.modern_gui import ModernCarParkGUI
    from src.models import ParkingSpace
except ImportError:
    # Intentar importación directa si falla la relativa
    import modern_gui
    import models
    ModernCarParkGUI = modern_gui.ModernCarParkGUI
    ParkingSpace = models.ParkingSpace

def test_tab_switching_and_spaces():
    """Prueba el cambio de pestañas y carga de espacios"""
    print("=== Prueba de Cambio de Pestañas y Carga de Espacios ===")
    
    # Crear ventana principal
    root = tk.Tk()
    
    try:
        # Crear GUI
        app = ModernCarParkGUI(root)
        
        # Cargar video de prueba
        video_path = "assets/carPark.mp4"
        if os.path.exists(video_path):
            print(f"Cargando video: {video_path}")
            app.load_video_file(video_path)
            root.update()
            time.sleep(0.5)
        else:
            print("Video no encontrado, usando imagen por defecto")
        
        # Cargar espacios legacy si existe
        spaces_path = "assets/CarParkPos"
        if os.path.exists(spaces_path):
            print(f"Cargando espacios: {spaces_path}")
            
            # Simular la carga de espacios
            try:
                import pickle
                with open(spaces_path, 'rb') as f:
                    positions = pickle.load(f)
                
                from models import ParkingSpace
                spaces = []
                default_width = 107
                default_height = 48
                
                for i, pos in enumerate(positions):
                    if len(pos) >= 2:
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
                
                # Asignar espacios
                app.spaces = spaces
                print(f"✅ Cargados {len(spaces)} espacios")
                
                # Forzar actualización de displays
                app.force_update_all_displays()
                root.update()
                
            except Exception as e:
                print(f"Error cargando espacios: {e}")
        
        # Simular cambio de pestañas
        print("\n=== Probando cambio de pestañas ===")
        
        # Ir al editor de espacios
        print("Cambiando a Editor de Espacios...")
        app.main_notebook.select(1)  # Pestaña del editor
        app.on_tab_changed(None)
        root.update()
        time.sleep(0.5)
        
        # Volver al dashboard
        print("Volviendo al Dashboard...")
        app.main_notebook.select(0)  # Pestaña principal
        app.on_tab_changed(None)
        root.update()
        time.sleep(0.5)
        
        # Probar actualización de video display
        print("\n=== Probando actualización de video display ===")
        app.safe_update_video_display()
        root.update()
        
        print("\n✅ Pruebas completadas sin errores críticos")
        print("La GUI debería mostrar correctamente:")
        print("- Video/imagen en el panel principal")
        print("- Espacios dibujados si se cargaron")
        print("- Cambio de pestañas sin errores")
        
        # Mantener la ventana abierta por unos segundos para inspección visual
        print("\nMantener ventana abierta por 5 segundos para inspección...")
        root.after(5000, root.quit)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    test_tab_switching_and_spaces()
