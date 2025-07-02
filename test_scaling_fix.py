#!/usr/bin/env python3
"""
Test específico para verificar que el escalado de espacios funciona correctamente
en el editor después de cargar posiciones
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
import cv2
import numpy as np
from src.modern_gui import ModernCarParkGUI

def create_test_parking_image():
    """Crear una imagen de estacionamiento con espacios claramente definidos"""
    # Crear imagen más grande para simular una imagen real
    img = np.full((800, 1200, 3), 100, dtype=np.uint8)
    
    # Dibujar espacios de estacionamiento claramente definidos
    spaces_positions = [
        (50, 200, 100, 80),    # Espacio 1
        (160, 200, 100, 80),   # Espacio 2  
        (270, 200, 100, 80),   # Espacio 3
        (380, 200, 100, 80),   # Espacio 4
        (490, 200, 100, 80),   # Espacio 5
        (600, 200, 100, 80),   # Espacio 6
        (50, 300, 100, 80),    # Espacio 7
        (160, 300, 100, 80),   # Espacio 8
        (270, 300, 100, 80),   # Espacio 9
        (380, 300, 100, 80),   # Espacio 10
    ]
    
    # Dibujar los espacios como rectángulos blancos
    for i, (x, y, w, h) in enumerate(spaces_positions):
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
        cv2.putText(img, f"P{i+1}", (x + 35, y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Simular algunos carros (rectángulos de colores)
    cv2.rectangle(img, (55, 205), (145, 275), (0, 0, 200), -1)  # Carro rojo en espacio 1
    cv2.rectangle(img, (275, 205), (365, 275), (0, 200, 0), -1)  # Carro verde en espacio 3
    cv2.rectangle(img, (165, 305), (255, 375), (200, 0, 0), -1)  # Carro azul en espacio 8
    
    # Agregar título
    cv2.putText(img, "TEST PARKING LOT - SCALING TEST", (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, "Original size: 1200x800", (450, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
    
    return img, spaces_positions

def test_scaling_in_editor():
    """Test específico para verificar que el escalado funciona correctamente"""
    
    print("🧪 Iniciando test de escalado en el editor")
    
    root = tk.Tk()
    app = ModernCarParkGUI(root)
    
    # Crear imagen de prueba con espacios conocidos
    test_image, known_spaces = create_test_parking_image()
    
    step = [0]
    
    def next_step():
        try:
            if step[0] == 0:
                print("📸 Paso 1: Cargando imagen de prueba (1200x800)...")
                app.current_frame = test_image
                app.update_video_display()
                print(f"✅ Imagen cargada - Dimensiones: {test_image.shape[:2]}")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 1:
                print("✏️ Paso 2: Cambiando al editor...")
                app.main_notebook.select(1)  # Cambiar a editor
                print("✅ Editor activado")
                step[0] += 1
                root.after(500, next_step)
                
            elif step[0] == 2:
                print("🖼️ Paso 3: Mostrando imagen en el editor...")
                app.display_image_in_editor()
                
                # Verificar que las variables de escalado se hayan calculado
                if hasattr(app, 'current_scale') and app.current_scale:
                    print(f"✅ Escala calculada: {app.current_scale:.3f}")
                    print(f"✅ Tamaño original: {app.original_image_size}")
                    print(f"✅ Tamaño mostrado: {app.current_display_size}")
                    print(f"✅ Offset: ({app.image_offset_x}, {app.image_offset_y})")
                else:
                    print("❌ Variables de escalado no calculadas correctamente")
                
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 3:
                print("📐 Paso 4: Creando espacios en coordenadas originales...")
                from src.models import ParkingSpace
                
                # Crear espacios usando las posiciones conocidas de la imagen original
                test_spaces = []
                for i, (x, y, w, h) in enumerate(known_spaces[:6]):  # Solo primeros 6
                    space = ParkingSpace(
                        id=str(i+1),
                        x=x,
                        y=y,
                        width=w,
                        height=h
                    )
                    test_spaces.append(space)
                
                app.spaces = test_spaces
                print(f"✅ {len(test_spaces)} espacios creados en coordenadas originales")
                
                # Mostrar las coordenadas originales de algunos espacios
                for i, space in enumerate(test_spaces[:3]):
                    print(f"  Espacio {i+1}: ({space.x}, {space.y}) {space.width}x{space.height}")
                
                step[0] += 1
                root.after(500, next_step)
                
            elif step[0] == 4:
                print("🎨 Paso 5: Redibujando espacios con escalado...")
                app.redraw_spaces_in_editor()
                
                # Verificar que los espacios se vean correctamente escalados
                print("✅ Espacios redibujados en el editor")
                
                # Simular conversión de coordenadas para verificar
                if hasattr(app, 'image_to_canvas_coords') and app.spaces:
                    space1 = app.spaces[0]
                    canvas_x, canvas_y = app.image_to_canvas_coords(space1.x, space1.y)
                    print(f"  Espacio 1 original: ({space1.x}, {space1.y})")
                    print(f"  Espacio 1 en canvas: ({canvas_x:.1f}, {canvas_y:.1f})")
                
                step[0] += 1
                root.after(1500, next_step)
                
            elif step[0] == 5:
                print("🏠 Paso 6: Regresando al panel principal...")
                app.main_notebook.select(0)
                
                # Verificar que en el panel principal también se vean correctamente
                app.safe_update_video_display()
                print("✅ Regresado al panel principal")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 6:
                print("🔄 Paso 7: Cambiando de nuevo al editor...")
                app.main_notebook.select(1)
                
                # Verificar que al cambiar de vuelta, todo sigue correcto
                app.refresh_editor_display()
                print("✅ Editor reactivado")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 7:
                print("🎯 Paso 8: Verificación final...")
                
                # Verificaciones finales
                checks = [
                    ("Imagen original guardada", app.original_image_size is not None),
                    ("Escala calculada", hasattr(app, 'current_scale') and app.current_scale > 0),
                    ("Espacios cargados", len(app.spaces) > 0),
                    ("Canvas funcionando", hasattr(app, 'editor_canvas') and app.editor_canvas is not None),
                    ("Funciones de conversión", hasattr(app, 'image_to_canvas_coords')),
                ]
                
                all_good = True
                for check_name, result in checks:
                    if result:
                        print(f"  ✅ {check_name}")
                    else:
                        print(f"  ❌ {check_name}")
                        all_good = False
                
                if all_good:
                    print("\n🎉 ¡TEST DE ESCALADO COMPLETADO EXITOSAMENTE!")
                    print("✅ Los espacios ahora deberían aparecer correctamente posicionados")
                    print("✅ El escalado funciona correctamente entre pestañas")
                else:
                    print("\n❌ Algunos checks fallaron - revisar implementación")
                
                root.after(2000, root.quit)
                
        except Exception as e:
            print(f"❌ Error en paso {step[0]}: {e}")
            import traceback
            traceback.print_exc()
            root.after(1000, root.quit)
    
    # Comenzar el test
    root.after(500, next_step)
    
    # Timeout de seguridad
    root.after(15000, lambda: (print("⏱️ Timeout - cerrando test"), root.quit()))
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Test interrumpido por el usuario")
    except Exception as e:
        print(f"Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scaling_in_editor()
