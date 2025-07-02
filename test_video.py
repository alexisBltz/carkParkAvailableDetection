"""
Script de prueba rápida para verificar la funcionalidad de video
"""
import cv2
import os

def test_video_load():
    """Prueba de carga de video simple"""
    
    # Buscar archivos de video en assets
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    assets_dir = 'assets'
    
    if os.path.exists(assets_dir):
        print(f"📁 Buscando videos en {assets_dir}/")
        video_files = []
        
        for file in os.listdir(assets_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(os.path.join(assets_dir, file))
        
        if video_files:
            print(f"🎬 Videos encontrados:")
            for video in video_files:
                print(f"   • {video}")
                
                # Probar carga del video
                cap = cv2.VideoCapture(video)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"   ✅ {os.path.basename(video)} - Carga exitosa")
                        print(f"      Dimensiones: {frame.shape[1]}x{frame.shape[0]}")
                        print(f"      FPS: {cap.get(cv2.CAP_PROP_FPS):.1f}")
                    else:
                        print(f"   ❌ {os.path.basename(video)} - No se pudo leer frame")
                    cap.release()
                else:
                    print(f"   ❌ {os.path.basename(video)} - No se pudo abrir")
        else:
            print("❌ No se encontraron videos en assets/")
    else:
        print("❌ Carpeta assets/ no encontrada")
    
    # Probar cámara
    print("\n📹 Probando cámara...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✅ Cámara funcional")
            print(f"   Resolución: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print("⚠️ Cámara disponible pero sin frame")
        cap.release()
    else:
        print("❌ No se pudo acceder a la cámara")

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 CarPark - Prueba de Video")
    print("=" * 50)
    test_video_load()
    print("\n✅ Prueba completada")
    print("💡 Si encuentras videos, prueba cargarlos en la aplicación principal")
