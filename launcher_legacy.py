"""
Launcher Legacy - Ejecutor independiente de las funcionalidades legacy
Permite probar las funcionalidades del código original de forma directa
"""
import sys
import os
import argparse

# Agregar el directorio src al path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, current_dir)

def run_space_editor(image_path: str):
    """Ejecuta el editor de espacios legacy"""
    try:
        from src.legacy_detector import LegacySpaceEditor
        
        editor = LegacySpaceEditor(image_path)
        print(f"🎯 Iniciando editor de espacios para: {image_path}")
        editor.start_editing()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de que opencv-python esté instalado: pip install opencv-python")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_video_analysis(video_path: str):
    """Ejecuta el análisis de video legacy"""
    try:
        from src.legacy_detector import LegacyVideoProcessor
        
        if not os.path.exists("CarParkPos"):
            print("❌ Archivo CarParkPos no encontrado.")
            print("Ejecuta primero el editor de espacios con una imagen del estacionamiento.")
            return
        
        processor = LegacyVideoProcessor(video_path)
        print(f"🎬 Iniciando análisis de video: {video_path}")
        processor.play_video()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de que todas las dependencias estén instaladas: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_files():
    """Verifica que los archivos necesarios existan"""
    files_to_check = [
        "assets/carParkImg.png",
        "assets/carPark.mp4"
    ]
    
    print("🔍 Verificando archivos necesarios:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - No encontrado")
    
    if os.path.exists("CarParkPos"):
        print("✅ CarParkPos - Archivo de espacios encontrado")
    else:
        print("⚠️  CarParkPos - Archivo de espacios no encontrado (se creará al usar el editor)")

def main():
    """Función principal del launcher"""
    parser = argparse.ArgumentParser(description="CarPark Legacy Launcher")
    parser.add_argument("mode", choices=["editor", "video", "check"], 
                       help="Modo de ejecución")
    parser.add_argument("--image", "-i", help="Ruta de la imagen para el editor")
    parser.add_argument("--video", "-v", help="Ruta del video para análisis")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚗 CarPark Legacy Launcher")
    print("🔧 Funcionalidades del algoritmo original")
    print("=" * 60)
    
    if args.mode == "check":
        check_files()
        
    elif args.mode == "editor":
        image_path = args.image or "assets/carParkImg.png"
        if not os.path.exists(image_path):
            print(f"❌ Imagen no encontrada: {image_path}")
            print("Usa --image para especificar la ruta correcta")
            return
        run_space_editor(image_path)
        
    elif args.mode == "video":
        video_path = args.video or "assets/carPark.mp4"
        if not os.path.exists(video_path):
            print(f"❌ Video no encontrado: {video_path}")
            print("Usa --video para especificar la ruta correcta")
            return
        run_video_analysis(video_path)

def run_interactive():
    """Modo interactivo si no se proporcionan argumentos"""
    print("=" * 60)
    print("🚗 CarPark Legacy - Modo Interactivo")
    print("🔧 Funcionalidades del algoritmo original")
    print("=" * 60)
    
    while True:
        print("\nOpciones disponibles:")
        print("1. 📝 Editor de espacios")
        print("2. 🎬 Análisis de video")
        print("3. 🔍 Verificar archivos")
        print("4. ❌ Salir")
        
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == "1":
            image_path = input("Ruta de la imagen (Enter para assets/carParkImg.png): ").strip()
            if not image_path:
                image_path = "assets/carParkImg.png"
            
            if os.path.exists(image_path):
                run_space_editor(image_path)
            else:
                print(f"❌ Imagen no encontrada: {image_path}")
                
        elif choice == "2":
            video_path = input("Ruta del video (Enter para assets/carPark.mp4): ").strip()
            if not video_path:
                video_path = "assets/carPark.mp4"
            
            if os.path.exists(video_path):
                run_video_analysis(video_path)
            else:
                print(f"❌ Video no encontrado: {video_path}")
                
        elif choice == "3":
            check_files()
            
        elif choice == "4":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        run_interactive()
