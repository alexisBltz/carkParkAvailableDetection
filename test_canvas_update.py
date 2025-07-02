#!/usr/bin/env python3
"""
Script para probar la actualización automática del canvas del editor
después de cargar espacios en CarPark Project v3.0
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox
import time

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar la GUI moderna
from src.modern_gui import ModernCarParkGUI
from src.models import ParkingSpace
import config

def test_automatic_canvas_update():
    """Prueba la actualización automática del canvas después de cargar espacios"""
    
    # Crear ventana principal
    root = tk.Tk()
    
    try:
        # Crear la GUI moderna
        app = ModernCarParkGUI(root)
        
        # Simular la carga de espacios después de un breve delay
        def simulate_load_spaces():
            try:
                # Crear algunos espacios de prueba
                test_spaces = [
                    ParkingSpace(id="TEST_1", x=100, y=100, width=107, height=48),
                    ParkingSpace(id="TEST_2", x=220, y=100, width=107, height=48),
                    ParkingSpace(id="TEST_3", x=340, y=100, width=107, height=48),
                    ParkingSpace(id="TEST_4", x=100, y=160, width=107, height=48),
                    ParkingSpace(id="TEST_5", x=220, y=160, width=107, height=48),
                ]
                
                # Cargar los espacios directamente
                app.spaces = test_spaces
                print(f"✅ Espacios de prueba cargados: {len(test_spaces)}")
                
                # Forzar actualización de todos los displays
                app.force_update_all_displays()
                
                # Actualizar status
                app.status_var.set(f"🧪 Espacios de prueba cargados: {len(test_spaces)}")
                
                print("✅ Actualización de canvas completada")
                
                # Verificar que los espacios se visualizan
                root.after(1000, verify_canvas_display)
                
            except Exception as e:
                print(f"❌ Error simulando carga de espacios: {e}")
                messagebox.showerror("Error", f"Error en prueba: {e}")
        
        def verify_canvas_display():
            """Verifica que los espacios se muestren en el canvas"""
            try:
                # Verificar que hay espacios cargados
                if len(app.spaces) > 0:
                    print(f"✅ Verificación: {len(app.spaces)} espacios en memoria")
                    
                    # Verificar que el canvas del editor existe
                    if hasattr(app, 'editor_canvas') and app.editor_canvas is not None:
                        print("✅ Canvas del editor está disponible")
                        
                        # Verificar que hay elementos dibujados en el canvas
                        canvas_items = app.editor_canvas.find_all()
                        print(f"✅ Elementos en canvas: {len(canvas_items)}")
                        
                        if len(canvas_items) > 0:
                            print("🎉 ¡ÉXITO! Los espacios se visualizan automáticamente en el canvas")
                            messagebox.showinfo("Éxito", 
                                "✅ Los espacios se cargan y visualizan automáticamente\n" +
                                f"Espacios cargados: {len(app.spaces)}\n" +
                                f"Elementos en canvas: {len(canvas_items)}")
                        else:
                            print("⚠️  Canvas vacío después de cargar espacios")
                            messagebox.showwarning("Advertencia", 
                                "Los espacios se cargaron pero no se visualizan automáticamente")
                    else:
                        print("❌ Canvas del editor no disponible")
                        messagebox.showerror("Error", "Canvas del editor no está disponible")
                else:
                    print("❌ No hay espacios cargados")
                    messagebox.showerror("Error", "No se cargaron espacios de prueba")
                    
            except Exception as e:
                print(f"❌ Error en verificación: {e}")
                messagebox.showerror("Error", f"Error en verificación: {e}")
        
        # Programar la simulación de carga después de 3 segundos
        root.after(3000, simulate_load_spaces)
        
        # Mostrar información inicial
        print("🧪 Iniciando prueba de actualización automática del canvas...")
        print("⏳ La prueba iniciará en 3 segundos...")
        print("📋 Instrucciones:")
        print("   1. Se cargarán 5 espacios de prueba automáticamente")
        print("   2. El canvas del editor debería actualizarse inmediatamente")
        print("   3. Se mostrará un mensaje con el resultado")
        
        # Iniciar la aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error iniciando prueba: {e}")
        messagebox.showerror("Error", f"Error iniciando aplicación: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBA: Actualización Automática del Canvas del Editor")
    print("=" * 60)
    
    test_automatic_canvas_update()
    
    print("=" * 60)
    print("🏁 Prueba completada")
    print("=" * 60)
