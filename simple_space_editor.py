#!/usr/bin/env python3
"""
Editor Simple de Espacios de Estacionamiento
Basado en el enfoque directo y eficaz del ParkingSpacePicker original
"""
import cv2
import pickle
import os
import sys

# Configuración de espacios
SPACE_WIDTH = 107
SPACE_HEIGHT = 48
PARKING_POSITIONS_FILE = 'assets/CarParkPos'
PARKING_IMAGE_FILE = 'assets/carParkImg.png'

class SimpleParkingEditor:
    """Editor simple de espacios de estacionamiento"""
    
    def __init__(self):
        self.pos_list = []
        self.image = None
        self.window_name = "Editor de Espacios - Click Izq: Agregar | Click Der: Eliminar | ESC: Salir"
        self.load_existing_positions()
        self.load_image()
    
    def load_existing_positions(self):
        """Carga posiciones existentes si el archivo existe"""
        try:
            if os.path.exists(PARKING_POSITIONS_FILE):
                with open(PARKING_POSITIONS_FILE, 'rb') as f:
                    self.pos_list = pickle.load(f)
                print(f"✅ Cargadas {len(self.pos_list)} posiciones existentes")
            else:
                self.pos_list = []
                print("ℹ️  No hay posiciones existentes. Comenzando desde cero.")
        except Exception as e:
            print(f"⚠️  Error cargando posiciones: {e}")
            self.pos_list = []
    
    def load_image(self):
        """Carga la imagen del estacionamiento"""
        if not os.path.exists(PARKING_IMAGE_FILE):
            print(f"❌ No se encontró la imagen: {PARKING_IMAGE_FILE}")
            print("📁 Asegúrate de que la imagen esté en la carpeta assets/")
            return False
        
        self.image = cv2.imread(PARKING_IMAGE_FILE)
        if self.image is None:
            print(f"❌ No se pudo cargar la imagen: {PARKING_IMAGE_FILE}")
            return False
        
        print(f"✅ Imagen cargada: {self.image.shape}")
        return True
    
    def save_positions(self):
        """Guarda las posiciones en el archivo"""
        try:
            # Crear directorio assets si no existe
            os.makedirs(os.path.dirname(PARKING_POSITIONS_FILE), exist_ok=True)
            
            with open(PARKING_POSITIONS_FILE, 'wb') as f:
                pickle.dump(self.pos_list, f)
            print(f"💾 Guardadas {len(self.pos_list)} posiciones")
        except Exception as e:
            print(f"❌ Error guardando posiciones: {e}")
    
    def mouse_callback(self, event, x, y, flags, param):
        """Callback para eventos del mouse"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Click izquierdo: agregar espacio
            self.pos_list.append((x, y))
            print(f"➕ Espacio agregado en ({x}, {y}). Total: {len(self.pos_list)}")
            self.save_positions()
            
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Click derecho: eliminar espacio
            for i, (px, py) in enumerate(self.pos_list):
                if px < x < px + SPACE_WIDTH and py < y < py + SPACE_HEIGHT:
                    removed_pos = self.pos_list.pop(i)
                    print(f"➖ Espacio eliminado de {removed_pos}. Total: {len(self.pos_list)}")
                    self.save_positions()
                    break
    
    def draw_spaces(self, img):
        """Dibuja todos los espacios en la imagen"""
        display_img = img.copy()
        
        for i, (x, y) in enumerate(self.pos_list):
            # Color alternativo para mejor visibilidad
            color = (255, 0, 255) if i % 2 == 0 else (255, 255, 0)  # Magenta/Amarillo
            
            # Dibujar rectángulo del espacio
            cv2.rectangle(display_img, (x, y), (x + SPACE_WIDTH, y + SPACE_HEIGHT), color, 2)
            
            # Dibujar número del espacio
            cv2.putText(display_img, str(i), (x + 5, y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Información en pantalla
        info_text = f"Espacios: {len(self.pos_list)} | Click Izq: Agregar | Click Der: Eliminar"
        cv2.putText(display_img, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        instructions = "Presiona ESC para salir | TAB para ayuda"
        cv2.putText(display_img, instructions, (10, display_img.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        return display_img
    
    def show_help(self):
        """Muestra ayuda en consola"""
        print("\n" + "="*50)
        print("📖 AYUDA - Editor de Espacios")
        print("="*50)
        print("🖱️  CONTROLES:")
        print("   • Click Izquierdo:  Agregar nuevo espacio")
        print("   • Click Derecho:    Eliminar espacio existente")
        print("   • ESC:              Salir del editor")
        print("   • TAB:              Mostrar esta ayuda")
        print("")
        print("📏 CONFIGURACIÓN ACTUAL:")
        print(f"   • Ancho del espacio:  {SPACE_WIDTH} px")
        print(f"   • Alto del espacio:   {SPACE_HEIGHT} px")
        print(f"   • Espacios definidos: {len(self.pos_list)}")
        print("")
        print("📁 ARCHIVOS:")
        print(f"   • Imagen: {PARKING_IMAGE_FILE}")
        print(f"   • Posiciones: {PARKING_POSITIONS_FILE}")
        print("="*50 + "\n")
    
    def run(self):
        """Ejecuta el editor"""
        if self.image is None:
            return False
        
        print("\n🚗 Editor Simple de Espacios de Estacionamiento")
        print("="*50)
        print("📖 Presiona TAB para ver la ayuda completa")
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        # Redimensionar ventana para mejor visualización
        cv2.resizeWindow(self.window_name, 1200, 800)
        
        while True:
            # Dibujar espacios
            display_img = self.draw_spaces(self.image)
            cv2.imshow(self.window_name, display_img)
            
            # Esperar tecla
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == 9:  # TAB
                self.show_help()
        
        cv2.destroyAllWindows()
        
        print(f"\n✅ Editor cerrado. Total de espacios: {len(self.pos_list)}")
        return True

def main():
    """Función principal"""
    print("🚗 Editor Simple de Espacios de Estacionamiento")
    print("Basado en el enfoque eficaz del ParkingSpacePicker original")
    print("-" * 60)
    
    # Verificar dependencias básicas
    try:
        import cv2
        import pickle
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("📦 Instala OpenCV con: pip install opencv-python")
        return
    
    # Verificar archivos
    if not os.path.exists(PARKING_IMAGE_FILE):
        print(f"❌ No se encontró la imagen: {PARKING_IMAGE_FILE}")
        print("📁 Coloca tu imagen del estacionamiento en assets/carParkImg.png")
        return
    
    # Crear editor y ejecutar
    editor = SimpleParkingEditor()
    success = editor.run()
    
    if success:
        print("\n🎯 SIGUIENTE PASO:")
        print("   Ejecuta test_simple_analyzer.py para probar el análisis")
        print("   con los espacios que acabas de definir.")
    
    print("\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Editor interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
