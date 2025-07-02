"""
Test Simple - Prueba las funcionalidades básicas del sistema
Réplica simplificada del código original con mejoras
"""
import cv2
import pickle
import numpy as np
import os

# Configuración
WIDTH, HEIGHT = 107, 48
POSITIONS_FILE = "CarParkPos"
IMAGE_FILE = "assets/carParkImg.png"
VIDEO_FILE = "assets/carPark.mp4"

def load_positions():
    """Carga las posiciones desde archivo"""
    try:
        if os.path.exists(POSITIONS_FILE):
            with open(POSITIONS_FILE, 'rb') as f:
                pos_list = pickle.load(f)
            print(f"✅ Cargadas {len(pos_list)} posiciones")
            return pos_list
        else:
            print("📁 Archivo de posiciones no encontrado")
            return []
    except Exception as e:
        print(f"❌ Error cargando posiciones: {e}")
        return []

def save_positions(pos_list):
    """Guarda las posiciones en archivo"""
    try:
        with open(POSITIONS_FILE, 'wb') as f:
            pickle.dump(pos_list, f)
        print(f"💾 Guardadas {len(pos_list)} posiciones")
    except Exception as e:
        print(f"❌ Error guardando posiciones: {e}")

def mouse_click(event, x, y, flags, params):
    """Maneja los clics del mouse para editar espacios"""
    pos_list = params['pos_list']
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Clic izquierdo: agregar espacio
        pos_list.append((x, y))
        print(f"➕ Agregado espacio en ({x}, {y})")
        save_positions(pos_list)
        
    elif event == cv2.EVENT_RBUTTONDOWN:
        # Clic derecho: eliminar espacio
        for i, pos in enumerate(pos_list):
            x1, y1 = pos
            if x1 < x < x1 + WIDTH and y1 < y < y1 + HEIGHT:
                removed_pos = pos_list.pop(i)
                print(f"➖ Eliminado espacio en {removed_pos}")
                save_positions(pos_list)
                break

def run_space_editor():
    """Ejecuta el editor de espacios"""
    if not os.path.exists(IMAGE_FILE):
        print(f"❌ Imagen no encontrada: {IMAGE_FILE}")
        return
    
    pos_list = load_positions()
    params = {'pos_list': pos_list}
    
    print("🖼️  Editor de espacios iniciado:")
    print("   • Clic izquierdo: Agregar espacio")
    print("   • Clic derecho: Eliminar espacio")
    print("   • Tecla 'q': Salir")
    
    while True:
        img = cv2.imread(IMAGE_FILE)
        
        # Dibujar espacios existentes
        for i, pos in enumerate(pos_list):
            cv2.rectangle(img, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), (255, 0, 255), 2)
            # Mostrar número del espacio
            cv2.putText(img, str(i + 1), (pos[0] + 5, pos[1] + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Mostrar información
        info_text = f"Espacios: {len(pos_list)} | Tamaño: {WIDTH}x{HEIGHT}"
        cv2.putText(img, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow("Editor de Espacios - CarPark", img)
        cv2.setMouseCallback("Editor de Espacios - CarPark", mouse_click, params)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cv2.destroyAllWindows()
    print("✅ Editor cerrado")

def check_parking_space(img_processed, pos_list):
    """Verifica la ocupación de los espacios"""
    space_counter = 0
    
    for i, pos in enumerate(pos_list):
        x, y = pos
        
        # Extraer región de interés
        img_crop = img_processed[y:y + HEIGHT, x:x + WIDTH]
        if img_crop.size == 0:
            continue
        
        # Contar píxeles no-cero
        count = cv2.countNonZero(img_crop)
        
        # Determinar ocupación (umbral de 900)
        if count < 900:
            color = (0, 255, 0)  # Verde para libre
            thickness = 5
            space_counter += 1
        else:
            color = (0, 0, 255)  # Rojo para ocupado
            thickness = 2
        
        return pos_list, space_counter, count, color, thickness
    
    return pos_list, space_counter, 0, (0, 255, 0), 2

def run_video_analysis():
    """Ejecuta el análisis de video"""
    if not os.path.exists(VIDEO_FILE):
        print(f"❌ Video no encontrado: {VIDEO_FILE}")
        return
    
    pos_list = load_positions()
    if not pos_list:
        print("❌ No hay espacios definidos. Ejecuta primero el editor.")
        return
    
    cap = cv2.VideoCapture(VIDEO_FILE)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir el video: {VIDEO_FILE}")
        return
    
    print("🎬 Análisis de video iniciado:")
    print("   • Tecla 'q': Salir")
    print("   • Tecla ESPACIO: Pausar/Reanudar")
    print("   • Tecla 'r': Reiniciar")
    
    paused = False
    
    while True:
        if not paused:
            # Verificar si llegamos al final del video
            if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reiniciar
            
            success, img = cap.read()
            if not success:
                break
            
            # Preprocesamiento (algoritmo original)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
            img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                 cv2.THRESH_BINARY_INV, 25, 16)
            img_median = cv2.medianBlur(img_threshold, 5)
            kernel = np.ones((3, 3), np.uint8)
            img_dilate = cv2.dilate(img_median, kernel, iterations=1)
            
            # Verificar espacios
            space_counter = 0
            for pos in pos_list:
                x, y = pos
                img_crop = img_dilate[y:y + HEIGHT, x:x + WIDTH]
                
                if img_crop.size == 0:
                    continue
                
                count = cv2.countNonZero(img_crop)
                
                if count < 900:
                    color = (0, 255, 0)  # Verde para libre
                    thickness = 5
                    space_counter += 1
                else:
                    color = (0, 0, 255)  # Rojo para ocupado
                    thickness = 2
                
                # Dibujar rectángulo
                cv2.rectangle(img, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), color, thickness)
                
                # Mostrar conteo
                cv2.putText(img, str(count), (x, y + HEIGHT - 3),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            # Mostrar resumen
            total_spaces = len(pos_list)
            cv2.putText(img, f'Libres: {space_counter}/{total_spaces}', (100, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 200, 0), 3)
            
            cv2.imshow("CarPark - Análisis de Video", img)
        
        # Manejar teclas
        key = cv2.waitKey(30 if not paused else 1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # Espacio para pausar/reanudar
            paused = not paused
            print(f"⏸️  Video {'pausado' if paused else 'reanudado'}")
        elif key == ord('r'):  # Reiniciar video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            paused = False
            print("🔄 Video reiniciado")
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Análisis finalizado")

def main():
    """Función principal"""
    print("=" * 60)
    print("🚗 CarPark Test Simple")
    print("🔧 Prueba básica del algoritmo original")
    print("=" * 60)
    
    while True:
        print("\nOpciones:")
        print("1. 📝 Editor de espacios")
        print("2. 🎬 Análisis de video")
        print("3. 📊 Mostrar información de archivos")
        print("4. ❌ Salir")
        
        choice = input("\nSelecciona (1-4): ").strip()
        
        if choice == "1":
            run_space_editor()
        elif choice == "2":
            run_video_analysis()
        elif choice == "3":
            print(f"\n📁 Archivos:")
            print(f"   Imagen: {IMAGE_FILE} {'✅' if os.path.exists(IMAGE_FILE) else '❌'}")
            print(f"   Video: {VIDEO_FILE} {'✅' if os.path.exists(VIDEO_FILE) else '❌'}")
            print(f"   Espacios: {POSITIONS_FILE} {'✅' if os.path.exists(POSITIONS_FILE) else '❌'}")
            if os.path.exists(POSITIONS_FILE):
                pos_list = load_positions()
                print(f"   Total espacios: {len(pos_list)}")
        elif choice == "4":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()
