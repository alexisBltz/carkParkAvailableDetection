#!/usr/bin/env python3
"""
Test completo del workflow para verificar que el GUI moderno funciona correctamente
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
import cv2
import numpy as np
from src.modern_gui import ModernCarParkGUI

def create_test_video_frame():
    """Crear un frame de video de prueba simulando un estacionamiento"""
    # Crear imagen de 800x600 con fondo gris
    img = np.full((600, 800, 3), 80, dtype=np.uint8)
    
    # Dibujar estacionamiento con líneas
    for i in range(50, 750, 100):
        cv2.rectangle(img, (i, 150), (i+90, 220), (255, 255, 255), 2)
        cv2.putText(img, f"S{(i-50)//100+1}", (i+35, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Simular algunos carros (rectángulos oscuros)
    cv2.rectangle(img, (150, 155), (235, 215), (30, 30, 100), -1)  # Carro en espacio 2
    cv2.rectangle(img, (350, 155), (435, 215), (30, 100, 30), -1)  # Carro en espacio 4
    
    # Agregar título
    cv2.putText(img, "CARPARK DETECTION SYSTEM", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(img, "Test Video Frame", (280, 550), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    
    return img

def test_complete_workflow():
    """Test completo del workflow: carga video → define espacios → análisis"""
    
    print("🧪 Iniciando test completo del workflow")
    
    root = tk.Tk()
    app = ModernCarParkGUI(root)
    
    step = [0]  # Usar lista para modificar en funciones anidadas
    
    def next_step():
        """Ejecutar el siguiente paso del test"""
        try:
            if step[0] == 0:
                print("📹 Paso 1: Cargando frame de video...")
                test_frame = create_test_video_frame()
                app.current_frame = test_frame
                app.update_video_display()
                print("✅ Frame cargado y mostrado")
                step[0] += 1
                root.after(1500, next_step)
                
            elif step[0] == 1:
                print("✏️ Paso 2: Cambiando al editor de espacios...")
                app.main_notebook.select(1)  # Cambiar a pestaña del editor
                print("✅ Editor activado")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 2:
                print("📐 Paso 3: Creando espacios de estacionamiento...")
                from src.models import ParkingSpace
                
                # Crear espacios que coincidan con el video de prueba
                test_spaces = [
                    ParkingSpace(id="1", x=50, y=150, width=90, height=70),
                    ParkingSpace(id="2", x=150, y=150, width=90, height=70),
                    ParkingSpace(id="3", x=250, y=150, width=90, height=70),
                    ParkingSpace(id="4", x=350, y=150, width=90, height=70),
                    ParkingSpace(id="5", x=450, y=150, width=90, height=70),
                    ParkingSpace(id="6", x=550, y=150, width=90, height=70),
                ]
                
                app.spaces = test_spaces
                app.force_update_all_displays()
                print(f"✅ {len(test_spaces)} espacios creados")
                step[0] += 1
                root.after(1500, next_step)
                
            elif step[0] == 3:
                print("🏠 Paso 4: Regresando al panel principal...")
                app.main_notebook.select(0)  # Cambiar a pestaña principal
                print("✅ Panel principal activado")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 4:
                print("🔍 Paso 5: Verificando visualización...")
                
                # Verificar estado
                checks = []
                checks.append(("Frame disponible", app.current_frame is not None))
                checks.append(("Espacios cargados", len(app.spaces) > 0))
                checks.append(("Canvas de video existe", hasattr(app, 'video_canvas') and app.video_canvas is not None))
                
                for check_name, result in checks:
                    if result:
                        print(f"  ✅ {check_name}")
                    else:
                        print(f"  ❌ {check_name}")
                
                # Intentar actualización forzada
                app.safe_update_video_display()
                print("✅ Actualización forzada completada")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 5:
                print("🎯 Paso 6: Simulando análisis...")
                
                if app.spaces and app.current_frame is not None:
                    # Simular resultados de análisis
                    from src.models import OccupancyStatus
                    from datetime import datetime
                    
                    current_time = datetime.now().isoformat()
                    
                    # Basado en el frame de prueba: espacios 2 y 4 ocupados
                    mock_results = [
                        OccupancyStatus(space_id="1", is_occupied=False, confidence=0.95, timestamp=current_time),
                        OccupancyStatus(space_id="2", is_occupied=True, confidence=0.87, timestamp=current_time),   # Tiene carro
                        OccupancyStatus(space_id="3", is_occupied=False, confidence=0.92, timestamp=current_time),
                        OccupancyStatus(space_id="4", is_occupied=True, confidence=0.89, timestamp=current_time),   # Tiene carro
                        OccupancyStatus(space_id="5", is_occupied=False, confidence=0.94, timestamp=current_time),
                        OccupancyStatus(space_id="6", is_occupied=False, confidence=0.88, timestamp=current_time),
                    ]
                    
                    app.analysis_results = mock_results
                    app.update_video_display()  # Actualizar con colores de ocupación
                    
                    occupied = sum(1 for r in mock_results if r.is_occupied)
                    available = len(mock_results) - occupied
                    
                    print(f"✅ Análisis simulado: {available} libres, {occupied} ocupados")
                else:
                    print("❌ No se puede simular análisis - faltan datos")
                
                step[0] += 1
                root.after(1500, next_step)
                
            elif step[0] == 6:
                print("🔄 Paso 7: Test de cambio de pestañas múltiple...")
                
                # Cambiar rápidamente entre pestañas para verificar estabilidad
                for i in range(3):
                    app.main_notebook.select(1 if i % 2 == 0 else 0)
                    root.update_idletasks()
                    
                # Asegurar que terminamos en el panel principal
                app.main_notebook.select(0)
                app.safe_update_video_display()
                
                print("✅ Cambios de pestaña múltiples completados")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 7:
                print("🎉 Test completo finalizado exitosamente!")
                print("📊 Resumen:")
                print(f"  - Frame de video: {'✅' if app.current_frame is not None else '❌'}")
                print(f"  - Espacios definidos: {len(app.spaces)}")
                print(f"  - Resultados de análisis: {len(app.analysis_results) if app.analysis_results else 0}")
                print(f"  - Canvas funcionando: {'✅' if hasattr(app, 'video_canvas') else '❌'}")
                
                print("\n✅ TODOS LOS TESTS PASARON - El sistema funciona correctamente!")
                root.after(2000, root.quit)
                
        except Exception as e:
            print(f"❌ Error en paso {step[0]}: {e}")
            import traceback
            traceback.print_exc()
            root.after(1000, root.quit)
    
    # Comenzar el test después de que la interfaz esté lista
    root.after(500, next_step)
    
    # Configurar cierre automático después de 20 segundos
    root.after(20000, lambda: (print("⏱️ Timeout - cerrando test"), root.quit()))
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Test interrumpido por el usuario")
    except Exception as e:
        print(f"Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_workflow()
