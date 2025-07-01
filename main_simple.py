#!/usr/bin/env python3
"""
CarPark Main Simple - Replica exacta del código que funciona
Basado en tu main.py exitoso
"""
import cv2
import pickle
import numpy as np
import os

# Configuración
VIDEO_PATH = 'assets/carPark.mp4'
POSITIONS_FILE = 'assets/CarParkPos'
width, height = 107, 48

def load_parking_positions():
    """Carga las posiciones de los espacios"""
    try:
        with open(POSITIONS_FILE, 'rb') as f:
            pos_list = pickle.load(f)
        print(f"✅ Cargadas {len(pos_list)} posiciones de espacios")
        return pos_list
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {POSITIONS_FILE}")
        print("💡 Ejecuta 'python simple_space_editor.py' para crear espacios")
        return []
    except Exception as e:
        print(f"❌ Error cargando posiciones: {e}")
        return []

def check_parking_space(img_processed, pos_list, img_display):
    """
    Función principal de análisis - EXACTA del main.py exitoso
    """
    space_counter = 0

    for pos in pos_list:
        x, y = pos

        # Extraer región del espacio (EXACTO como tu código)
        img_crop = img_processed[y:y + height, x:x + width]
        
        # Contar píxeles blancos (EXACTO como tu código)
        count = cv2.countNonZero(img_crop)

        # Lógica EXACTA de tu main.py
        if count < 900:
            color = (0, 255, 0)      # Verde = LIBRE
            thickness = 5
            space_counter += 1
        else:
            color = (0, 0, 255)      # Rojo = OCUPADO
            thickness = 2

        # Dibujar rectángulo (EXACTO como tu código)
        cv2.rectangle(img_display, pos, (pos[0] + width, pos[1] + height), color, thickness)
        
        # Mostrar conteo de píxeles
        cv2.putText(img_display, str(count), (x, y + height - 3), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Mostrar resumen total
    cv2.putText(img_display, f'Free: {space_counter}/{len(pos_list)}', (100, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 200, 0), 3)
    
    return space_counter

def main():
    """Función principal"""
    print("🚗 CarPark Project - Versión Simple que Funciona")
    print("Basada exactamente en tu main.py exitoso")
    print("=" * 50)
    
    # Verificar archivos
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video no encontrado: {VIDEO_PATH}")
        return
    
    # Cargar posiciones
    pos_list = load_parking_positions()
    if not pos_list:
        return
    
    # Abrir video
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir el video: {VIDEO_PATH}")
        return
    
    print(f"✅ Video abierto exitosamente")
    print(f"📹 Presiona 'q' para salir, 'r' para reiniciar video")
    
    frame_count = 0
    
    while True:
        # Loop infinito del video (EXACTO como tu código)
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        success, img = cap.read()
        if not success:
            break
        
        frame_count += 1
        
        # PREPROCESAMIENTO EXACTO de tu main.py
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV, 25, 16)
        img_median = cv2.medianBlur(img_threshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_median, kernel, iterations=1)

        # ANÁLISIS usando tu función exacta
        free_spaces = check_parking_space(img_dilate, pos_list, img)
        
        # Mostrar frame actual
        cv2.putText(img, f'Frame: {frame_count}', (10, img.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Mostrar resultado
        cv2.imshow("CarPark Analysis", img)
        
        # Controles de teclado
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reiniciar video
            print("🔄 Video reiniciado")
        elif key == ord('p'):
            # Pausa
            cv2.waitKey(0)
    
    # Limpiar
    cap.release()
    cv2.destroyAllWindows()
    print("\n👋 Aplicación cerrada")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Aplicación interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
