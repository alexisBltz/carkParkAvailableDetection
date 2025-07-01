#!/usr/bin/env python3
"""
CarPark Project - Versión Simple que Funciona
Basado exactamente en el código main.py que me pasaste
"""
import cv2
import pickle
import cvzone
import numpy as np
import os

class SimpleCarParkApp:
    """Aplicación simple basada en el código que realmente funciona"""
    
    def __init__(self):
        # Archivos
        self.video_path = 'assets/carPark.mp4'
        self.positions_file = 'assets/CarParkPos'
        self.image_path = 'assets/carParkImg.png'
        
        # Dimensiones de espacios (del código original)
        self.width = 107
        self.height = 48
        
        # Cargar posiciones
        self.pos_list = self.load_positions()
        
        # Video capture
        self.cap = None
        
    def load_positions(self):
        """Carga las posiciones de los espacios"""
        try:
            with open(self.positions_file, 'rb') as f:
                pos_list = pickle.load(f)
            print(f"✅ Cargadas {len(pos_list)} posiciones de espacios")
            return pos_list
        except Exception as e:
            print(f"❌ Error cargando posiciones: {e}")
            return []
    
    def setup_video(self):
        """Configura el video"""
        if not os.path.exists(self.video_path):
            print(f"❌ Video no encontrado: {self.video_path}")
            return False
        
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"❌ No se pudo abrir el video: {self.video_path}")
            return False
        
        print(f"✅ Video configurado: {self.video_path}")
        return True
    
    def check_parking_space(self, img_processed, original_img):
        """
        Función principal de análisis - EXACTAMENTE como el código que funciona
        """
        space_counter = 0
        
        for pos in self.pos_list:
            x, y = pos
            
            # Extraer crop de la imagen procesada
            img_crop = img_processed[y:y + self.height, x:x + self.width]
            
            # Contar píxeles no-cero (blancos)
            count = cv2.countNonZero(img_crop)
            
            # Lógica de detección EXACTA del código original
            if count < 900:
                color = (0, 255, 0)  # Verde = libre
                thickness = 5
                space_counter += 1
            else:
                color = (0, 0, 255)  # Rojo = ocupado
                thickness = 2
            
            # Dibujar rectángulo
            cv2.rectangle(original_img, pos, (pos[0] + self.width, pos[1] + self.height), color, thickness)
            
            # Mostrar conteo de píxeles
            cvzone.putTextRect(original_img, str(count), (x, y + self.height - 3), 
                             scale=1, thickness=2, offset=0, colorR=color)
        
        # Mostrar estadísticas generales
        cvzone.putTextRect(original_img, f'Free: {space_counter}/{len(self.pos_list)}', 
                         (100, 50), scale=3, thickness=5, offset=20, colorR=(0, 200, 0))
        
        return space_counter
    
    def process_frame(self, img):
        """
        Procesamiento de frame EXACTO del código original
        """
        # Paso 1: Convertir a escala de grises
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Paso 2: Gaussian Blur
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        
        # Paso 3: Adaptive Threshold
        img_threshold = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, 25, 16)
        
        # Paso 4: Median Blur
        img_median = cv2.medianBlur(img_threshold, 5)
        
        # Paso 5: Dilate
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_median, kernel, iterations=1)
        
        return img_dilate
    
    def run_video_analysis(self):
        """Ejecuta el análisis de video"""
        if not self.setup_video():
            return False
        
        if not self.pos_list:
            print("❌ No hay espacios definidos")
            return False
        
        print("🚗 Análisis de Video Iniciado")
        print("Presiona 'q' para salir")
        
        while True:
            # Reiniciar video cuando termine
            if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            success, img = self.cap.read()
            if not success:
                break
            
            # Procesar frame EXACTAMENTE como el código original
            img_processed = self.process_frame(img)
            
            # Analizar espacios
            free_spaces = self.check_parking_space(img_processed, img)
            
            # Mostrar resultado
            cv2.imshow("CarPark Analysis", img)
            
            # Opcional: mostrar imagen procesada para debug
            # cv2.imshow("Processed", img_processed)
            
            # Controles
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        print("✅ Análisis completado")
        return True
    
    def run_image_analysis(self):
        """Ejecuta análisis en imagen estática"""
        if not os.path.exists(self.image_path):
            print(f"❌ Imagen no encontrada: {self.image_path}")
            return False
        
        if not self.pos_list:
            print("❌ No hay espacios definidos")
            return False
        
        # Cargar imagen
        img = cv2.imread(self.image_path)
        if img is None:
            print(f"❌ No se pudo cargar la imagen")
            return False
        
        print(f"🖼️ Analizando imagen estática...")
        
        # Procesar imagen
        img_processed = self.process_frame(img)
        
        # Analizar espacios
        free_spaces = self.check_parking_space(img_processed, img)
        
        print(f"📊 Resultado: {free_spaces} espacios libres de {len(self.pos_list)}")
        
        # Mostrar resultado
        cv2.imshow("CarPark Analysis - Static", img)
        cv2.imshow("Processed Image", img_processed)
        
        print("Presiona cualquier tecla para cerrar...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return True

def main():
    """Función principal"""
    print("🚗 CarPark - Versión Simple que Funciona")
    print("=" * 50)
    
    # Verificar dependencias
    try:
        import cvzone
    except ImportError:
        print("❌ cvzone no está instalado")
        print("📦 Instala con: pip install cvzone")
        return
    
    # Crear aplicación
    app = SimpleCarParkApp()
    
    print("\n¿Qué quieres hacer?")
    print("1. Analizar video")
    print("2. Analizar imagen estática")
    print("3. Editor de espacios")
    
    choice = input("\nElige una opción (1-3): ").strip()
    
    if choice == "1":
        app.run_video_analysis()
    elif choice == "2":
        app.run_image_analysis()
    elif choice == "3":
        print("💡 Ejecuta: python simple_space_editor.py")
    else:
        print("❌ Opción no válida")

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
