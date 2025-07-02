#!/usr/bin/env python3
"""
Script de prueba para verificar el feedback visual inmediato
tras cargar espacios en la GUI moderna.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import time

# Agregar src al path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from modern_gui import ModernCarParkGUI
    from models import ParkingSpace
    import config
except ImportError as e:
    print(f"Error importando módulos: {e}")
    sys.exit(1)

def test_immediate_feedback():
    """
    Prueba el feedback visual inmediato al cargar espacios.
    """
    print("=== PRUEBA DE FEEDBACK VISUAL INMEDIATO ===")
    
    # Verificar archivos de prueba
    video_path = os.path.join(config.ASSETS_DIR, "carPark.mp4")
    spaces_path = os.path.join(config.ASSETS_DIR, "CarParkPos")
    
    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return False
    
    if not os.path.exists(spaces_path):
        print(f"❌ Archivo de espacios no encontrado: {spaces_path}")
        return False
    
    print(f"✅ Video encontrado: {video_path}")
    print(f"✅ Espacios encontrados: {spaces_path}")
    
    # Crear ventana principal
    root = tk.Tk()
    app = ModernCarParkGUI(root)
    
    def auto_test():
        """Realizar test automático después de que la GUI esté lista"""
        try:
            print("\n1. Cargando video...")
            
            # Simular carga de video
            if app.video_manager.load_video(video_path):
                frame = app.video_manager.get_frame()
                if frame is not None:
                    app.current_frame = frame
                    app.update_video_display()
                    app.refresh_editor_display()
                    print("✅ Video cargado correctamente")
                else:
                    print("❌ No se pudo obtener frame del video")
                    return
            else:
                print("❌ No se pudo cargar el video")
                return
            
            # Cambiar a pestaña de editor
            app.notebook.select(1)
            app.on_tab_changed(None)
            
            print("\n2. Cargando espacios legacy...")
            
            # Simular carga de espacios legacy
            try:
                import pickle
                with open(spaces_path, 'rb') as f:
                    positions = pickle.load(f)
                
                # Convertir a espacios modernos
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
                
                # Asignar espacios
                app.spaces = spaces
                print(f"✅ Cargados {len(spaces)} espacios")
                
                # Forzar actualización inmediata
                print("\n3. Forzando actualización inmediata...")
                app.refresh_editor_display()
                root.update_idletasks()
                
                # Verificar que los espacios se ven en el editor
                if hasattr(app, 'editor_canvas') and app.editor_canvas is not None:
                    # Contar elementos con tag "space"
                    space_items = app.editor_canvas.find_withtag("space")
                    print(f"✅ Espacios dibujados en canvas: {len(space_items)}")
                    
                    if len(space_items) > 0:
                        print("🎉 FEEDBACK VISUAL INMEDIATO FUNCIONANDO!")
                        
                        # Mostrar información adicional
                        print(f"\nInformación del test:")
                        print(f"- Espacios cargados: {len(spaces)}")
                        print(f"- Elementos dibujados: {len(space_items)}")
                        print(f"- Canvas editor: {app.editor_canvas}")
                        print(f"- Frame actual: {app.current_frame is not None}")
                        
                        messagebox.showinfo(
                            "Test Exitoso",
                            f"¡Feedback visual inmediato funciona!\n\n"
                            f"Espacios cargados: {len(spaces)}\n"
                            f"Elementos dibujados: {len(space_items)}\n"
                            f"Los espacios aparecen inmediatamente sin cambiar pestaña."
                        )
                    else:
                        print("❌ Los espacios no se están dibujando en el canvas")
                        messagebox.showerror(
                            "Test Fallido",
                            "Los espacios no aparecen en el canvas del editor.\n"
                            "El feedback visual inmediato no está funcionando."
                        )
                else:
                    print("❌ Canvas del editor no disponible")
                    
            except Exception as e:
                print(f"❌ Error cargando espacios: {e}")
                messagebox.showerror("Error", f"Error en test: {e}")
        
        except Exception as e:
            print(f"❌ Error en test automático: {e}")
            messagebox.showerror("Error", f"Error en test: {e}")
    
    # Programar test automático
    root.after(1000, auto_test)
    
    print("\n✅ GUI iniciada - Test automático en 1 segundo...")
    print("📝 Observa si los espacios aparecen inmediatamente en el editor")
    print("🎯 Sin necesidad de cambiar de pestaña")
    
    # Iniciar GUI
    root.mainloop()
    
    return True

if __name__ == "__main__":
    try:
        test_immediate_feedback()
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error en test: {e}")
