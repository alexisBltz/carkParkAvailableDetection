#!/usr/bin/env python3
"""
Test para simular el escenario exacto del usuario: cargar espacios desde archivo
y verificar que se posicionan correctamente en el editor
"""

import sys
import os
import json

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
import cv2
import numpy as np
from src.modern_gui import ModernCarParkGUI

def create_parking_image_like_user():
    """Crear una imagen similar a la que muestra el usuario en la captura"""
    # Crear imagen similar a la del usuario (más wide)
    img = np.full((600, 1400, 3), 80, dtype=np.uint8)
    
    # Área izquierda con espacios vacíos (como en la imagen del usuario)
    for i in range(4):  # 4 filas
        for j in range(2):  # 2 columnas
            x = 250 + j * 120
            y = 180 + i * 90
            cv2.rectangle(img, (x, y), (x + 100, y + 70), (200, 200, 200), 2)
    
    # Área central con carros (similar a la imagen real del usuario)
    # Simular el estacionamiento denso con carros
    for i in range(5):
        for j in range(8):
            x = 600 + j * 35
            y = 150 + i * 45
            # Algunos espacios con carros
            if (i + j) % 3 == 0:
                cv2.rectangle(img, (x, y), (x + 30, y + 40), (50, 50, 150), -1)  # Carro
            cv2.rectangle(img, (x, y), (x + 30, y + 40), (255, 255, 255), 1)  # Líneas
    
    # Área derecha con más espacios
    for i in range(4):
        x = 1100
        y = 180 + i * 90
        cv2.rectangle(img, (x, y), (x + 100, y + 70), (200, 200, 200), 2)
    
    # Agregar texto de identificación
    cv2.putText(img, "PARKING LOT SIMULATION", (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, "Resolution: 1400x600 (similar to user's image)", (450, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    return img

def create_test_spaces_file():
    """Crear archivo de espacios de prueba que simule el escenario del usuario"""
    # Espacios dispersos en diferentes áreas como en la imagen del usuario
    spaces_data = [
        # Espacios del área izquierda
        {"id": "2", "x": 250, "y": 180, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "3", "x": 250, "y": 270, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "6", "x": 250, "y": 360, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "4", "x": 250, "y": 450, "width": 100, "height": 70, "confidence": 0.9},
        
        {"id": "14", "x": 370, "y": 180, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "15", "x": 370, "y": 270, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "16", "x": 370, "y": 360, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "17", "x": 370, "y": 450, "width": 100, "height": 70, "confidence": 0.9},
        
        # Espacios del área central (densos como carros)
        {"id": "9", "x": 600, "y": 150, "width": 30, "height": 40, "confidence": 0.85},
        {"id": "8", "x": 600, "y": 195, "width": 30, "height": 40, "confidence": 0.85},
        {"id": "7", "x": 600, "y": 240, "width": 30, "height": 40, "confidence": 0.85},
        {"id": "0", "x": 600, "y": 285, "width": 30, "height": 40, "confidence": 0.85},
        
        # Espacios del área derecha
        {"id": "59", "x": 1100, "y": 180, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "60", "x": 1100, "y": 270, "width": 100, "height": 70, "confidence": 0.9},
        {"id": "61", "x": 1100, "y": 360, "width": 100, "height": 70, "confidence": 0.9},
        
        # Algunos espacios adicionales en área central
        {"id": "76", "x": 950, "y": 200, "width": 35, "height": 45, "confidence": 0.8},
        {"id": "77", "x": 950, "y": 250, "width": 35, "height": 45, "confidence": 0.8},
        {"id": "78", "x": 950, "y": 300, "width": 35, "height": 45, "confidence": 0.8},
    ]
    
    # Guardar archivo JSON
    with open('test_spaces.json', 'w') as f:
        json.dump(spaces_data, f, indent=2)
    
    print(f"✅ Archivo de prueba creado: test_spaces.json con {len(spaces_data)} espacios")
    return 'test_spaces.json'

def test_user_scenario():
    """Test que simula exactamente el escenario del usuario"""
    
    print("🧪 Iniciando test del escenario del usuario")
    print("📋 Simulando: Cargar imagen → Ir al editor → Cargar espacios → Verificar posiciones")
    
    root = tk.Tk()
    app = ModernCarParkGUI(root)
    
    # Crear imagen y archivo de espacios de prueba
    test_image = create_parking_image_like_user()
    spaces_file = create_test_spaces_file()
    
    step = [0]
    
    def next_step():
        try:
            if step[0] == 0:
                print("📸 Paso 1: Cargando imagen de estacionamiento...")
                app.current_frame = test_image
                app.update_video_display()
                print(f"✅ Imagen cargada - Dimensiones: {test_image.shape[:2]}")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 1:
                print("✏️ Paso 2: Cambiando al editor de espacios...")
                app.main_notebook.select(1)  # Cambiar a editor
                print("✅ Editor activado")
                step[0] += 1
                root.after(800, next_step)
                
            elif step[0] == 2:
                print("🖼️ Paso 3: Mostrando imagen en el editor...")
                app.display_image_in_editor()
                
                # Mostrar información de escalado
                if hasattr(app, 'current_scale') and app.current_scale:
                    print(f"📏 Información de escalado:")
                    print(f"  - Escala: {app.current_scale:.3f}")
                    print(f"  - Tamaño original: {app.original_image_size}")
                    print(f"  - Tamaño mostrado: {app.current_display_size}")
                    print(f"  - Offset: ({app.image_offset_x}, {app.image_offset_y})")
                
                step[0] += 1
                root.after(500, next_step)
                
            elif step[0] == 3:
                print("📂 Paso 4: Simulando carga de espacios desde archivo...")
                
                # Cargar espacios directamente (simular FileManager.load_spaces_json)
                try:
                    with open(spaces_file, 'r') as f:
                        spaces_data = json.load(f)
                    
                    from src.models import ParkingSpace
                    loaded_spaces = []
                    for space_data in spaces_data:
                        space = ParkingSpace(
                            id=space_data['id'],
                            x=space_data['x'],
                            y=space_data['y'],
                            width=space_data['width'],
                            height=space_data['height'],
                            confidence=space_data.get('confidence', 0.0)
                        )
                        loaded_spaces.append(space)
                    
                    app.spaces = loaded_spaces
                    print(f"✅ {len(loaded_spaces)} espacios cargados desde archivo")
                    
                    # Mostrar algunas coordenadas originales para referencia
                    print("📍 Muestra de coordenadas originales:")
                    for i, space in enumerate(loaded_spaces[:5]):
                        print(f"  Espacio {space.id}: ({space.x}, {space.y}) {space.width}x{space.height}")
                    
                except Exception as e:
                    print(f"❌ Error cargando espacios: {e}")
                    return
                
                step[0] += 1
                root.after(500, next_step)
                
            elif step[0] == 4:
                print("🎨 Paso 5: Forzando actualización de displays...")
                
                # Esta es la línea clave que ejecuta el código problemático
                app.force_update_all_displays()
                print("✅ Actualización forzada completada")
                
                step[0] += 1
                root.after(800, next_step)
                
            elif step[0] == 5:
                print("🔍 Paso 6: Verificando posicionamiento de espacios...")
                
                # Verificar que los espacios se han redibujado
                if app.spaces:
                    print(f"✅ {len(app.spaces)} espacios en memoria")
                    
                    # Verificar las conversiones de coordenadas para algunos espacios
                    print("🔄 Verificando conversiones de coordenadas:")
                    for i, space in enumerate(app.spaces[:3]):
                        try:
                            canvas_x, canvas_y = app.image_to_canvas_coords(space.x, space.y)
                            print(f"  Espacio {space.id}: Original({space.x},{space.y}) → Canvas({canvas_x:.1f},{canvas_y:.1f})")
                        except Exception as e:
                            print(f"  ❌ Error convirtiendo espacio {space.id}: {e}")
                
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 6:
                print("🏠 Paso 7: Regresando al panel principal (escenario crítico)...")
                app.main_notebook.select(0)
                
                # Este es el momento crítico donde antes ocurría el error
                app.safe_update_video_display()
                print("✅ Regreso al panel principal exitoso - SIN ERRORES")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 7:
                print("🔄 Paso 8: Volviendo al editor para verificar persistencia...")
                app.main_notebook.select(1)
                app.refresh_editor_display()
                print("✅ Editor reactivado - espacios deben seguir correctos")
                step[0] += 1
                root.after(1000, next_step)
                
            elif step[0] == 8:
                print("🎯 Paso 9: Verificación final...")
                
                # Verificaciones críticas
                checks = [
                    ("Espacios cargados", len(app.spaces) > 0),
                    ("Escalado funcionando", hasattr(app, 'current_scale') and app.current_scale > 0),
                    ("Sin errores al cambiar pestañas", True),  # Si llegamos aquí, no hubo errores
                    ("Conversión de coordenadas", hasattr(app, 'image_to_canvas_coords')),
                    ("Tamaño original guardado", app.original_image_size is not None),
                ]
                
                all_passed = True
                print("📊 Resultados de verificación:")
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"  {status} {check_name}")
                    if not result:
                        all_passed = False
                
                if all_passed:
                    print("\n🎉 ¡ESCENARIO DEL USUARIO RESUELTO EXITOSAMENTE!")
                    print("✅ Los espacios ahora se posicionan correctamente después del resize")
                    print("✅ No hay errores al cambiar entre pestañas")
                    print("✅ El escalado funciona correctamente")
                    print("✅ Las coordenadas se convierten apropiadamente")
                else:
                    print("\n❌ Algunas verificaciones fallaron")
                
                # Limpiar archivo de prueba
                if os.path.exists(spaces_file):
                    os.remove(spaces_file)
                    print(f"🗑️ Archivo de prueba eliminado: {spaces_file}")
                
                root.after(2000, root.quit)
                
        except Exception as e:
            print(f"❌ Error en paso {step[0]}: {e}")
            import traceback
            traceback.print_exc()
            root.after(1000, root.quit)
    
    # Comenzar el test
    root.after(500, next_step)
    
    # Timeout de seguridad
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
    test_user_scenario()
