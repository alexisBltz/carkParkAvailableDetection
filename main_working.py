#!/usr/bin/env python3
"""
Réplica EXACTA del main.py que funciona
Código simplificado sin clases, igual al original
"""
import cv2
import pickle
import cvzone
import numpy as np
import os

# Configuración (igual al código original)
width, height = 107, 48

def load_positions():
    """Carga posiciones de espacios"""
    try:
        with open('assets/CarParkPos', 'rb') as f:
            pos_list = pickle.load(f)
        print(f"✅ Cargadas {len(pos_list)} posiciones")
        return pos_list
    except Exception as e:
        print(f"❌ Error cargando posiciones: {e}")
        return []

def check_parking_space(img_pro, img_original, pos_list):
    """
    Función EXACTA del código original que funciona
    """
    space_counter = 0

    for pos in pos_list:
        x, y = pos

        img_crop = img_pro[y:y + height, x:x + width]
        count = cv2.countNonZero(img_crop)

        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            space_counter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img_original, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img_original, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img_original, f'Free: {space_counter}/{len(pos_list)}', (100, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))
    
    return space_counter

def run_video_analysis():
    """Análisis de video - código original"""
    print("🎥 Análisis de Video")
    
    # Verificar archivos
    video_path = 'assets/carPark.mp4'
    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return
    
    # Cargar posiciones
    pos_list = load_positions()
    if not pos_list:
        return
    
    # Video feed (igual al original)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ No se pudo abrir el video")
        return
    
    print("▶️  Reproduciendo video... Presiona 'q' para salir")
    
    while True:
        # Reiniciar video cuando termine (igual al original)
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        success, img = cap.read()
        if not success:
            break
        
        # Procesamiento EXACTO del código original
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV, 25, 16)
        img_median = cv2.medianBlur(img_threshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_median, kernel, iterations=1)

        # Análisis de espacios
        free_spaces = check_parking_space(img_dilate, img, pos_list)
        
        cv2.imshow("CarPark Video", img)
        
        # Opcional: mostrar procesamiento
        # cv2.imshow("Processed", img_dilate)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Video terminado")

def run_image_analysis():
    """Análisis de imagen estática"""
    print("🖼️ Análisis de Imagen")
    
    # Verificar archivos
    image_path = 'assets/carParkImg.png'
    if not os.path.exists(image_path):
        print(f"❌ Imagen no encontrada: {image_path}")
        return
    
    # Cargar posiciones
    pos_list = load_positions()
    if not pos_list:
        return
    
    # Cargar imagen
    img = cv2.imread(image_path)
    if img is None:
        print("❌ No se pudo cargar la imagen")
        return
    
    # Procesamiento EXACTO del código original
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
    img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    img_median = cv2.medianBlur(img_threshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    img_dilate = cv2.dilate(img_median, kernel, iterations=1)

    # Análisis de espacios
    free_spaces = check_parking_space(img_dilate, img, pos_list)
    
    print(f"📊 Resultado: {free_spaces} espacios libres de {len(pos_list)}")
    
    cv2.imshow("CarPark Image", img)
    cv2.imshow("Processed", img_dilate)
    
    print("Presiona cualquier tecla para cerrar...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    """Menú principal"""
    print("🚗 CarPark - Código Original que Funciona")
    print("=" * 45)
    
    # Verificar dependencias
    try:
        import cvzone
    except ImportError:
        print("❌ cvzone no instalado. Ejecuta: pip install cvzone")
        return
    
    print("\n¿Qué quieres hacer?")
    print("1. 🎥 Analizar video")
    print("2. 🖼️  Analizar imagen")
    print("3. 🖱️  Editor de espacios")
    
    choice = input("\nElige (1-3): ").strip()
    
    if choice == "1":
        run_video_analysis()
    elif choice == "2":
        run_image_analysis()
    elif choice == "3":
        print("💡 Para editar espacios ejecuta:")
        print("   python simple_space_editor.py")
    else:
        print("❌ Opción no válida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
