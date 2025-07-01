#!/usr/bin/env python3
"""
Prueba del analizador que REALMENTE funciona
Basado exactamente en el main.py exitoso que compariste
"""
import cv2
import numpy as np
import pickle
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.working_analyzer import WorkingOccupancyAnalyzer
from src.models import ParkingSpace

def load_spaces():
    """Carga espacios desde CarParkPos"""
    width, height = 107, 48  # Tamaños del código original
    
    try:
        with open('assets/CarParkPos', 'rb') as f:
            pos_list = pickle.load(f)
        
        spaces = []
        for i, (x, y) in enumerate(pos_list):
            space = ParkingSpace(
                id=f"space_{i}",
                x=x, y=y,
                width=width, height=height
            )
            spaces.append(space)
        
        return spaces
    except Exception as e:
        print(f"Error cargando espacios: {e}")
        return []

def test_working_analyzer():
    """Prueba el analizador que replica el código exitoso"""
    print("🚗 Prueba del Analizador que REALMENTE Funciona")
    print("Basado exactamente en el main.py exitoso")
    print("=" * 60)
    
    # Cargar imagen
    img = cv2.imread("assets/carParkImg.png")
    if img is None:
        print("❌ No se pudo cargar la imagen")
        return
    
    print(f"✅ Imagen cargada: {img.shape}")
    
    # Cargar espacios
    spaces = load_spaces()
    if not spaces:
        print("❌ No hay espacios")
        return
    
    print(f"✅ Espacios cargados: {len(spaces)}")
    
    # Probar diferentes umbrales de píxeles
    thresholds = [700, 800, 900, 1000, 1100, 1200]
    
    print(f"\n📊 Resultados por umbral de píxeles:")
    print("Umbral | Ocupados | Libres | Ratio")
    print("-" * 35)
    
    for threshold in thresholds:
        analyzer = WorkingOccupancyAnalyzer(pixel_threshold=threshold)
        results = analyzer.analyze_spaces(img, spaces)
        
        occupied = sum(1 for r in results if r.is_occupied)
        free = len(results) - occupied
        ratio = occupied / len(results) * 100
        
        marker = " ← ORIGINAL" if threshold == 900 else ""
        print(f"{threshold:6d} | {occupied:8d} | {free:6d} | {ratio:5.1f}%{marker}")
    
    # Análisis detallado con umbral original (900)
    print(f"\n🔍 Análisis detallado (umbral 900 - ORIGINAL):")
    analyzer = WorkingOccupancyAnalyzer(pixel_threshold=900)
    debug_results = analyzer.analyze_with_debug_info(img, spaces)
    
    print(f"Espacio | Píxeles | Estado")
    print("-" * 30)
    
    for debug_info in debug_results[:15]:  # Mostrar primeros 15
        if 'error' in debug_info:
            continue
        
        space_idx = debug_info['space_index']
        pixel_count = debug_info['pixel_count']
        status = debug_info['status']
        
        print(f"{space_idx:7d} | {pixel_count:7d} | {status}")
    
    # Mostrar frame procesado
    print(f"\n👀 Mostrando visualización... (presiona cualquier tecla para continuar)")
    
    # Frame original con análisis
    img_result = analyzer.visualize_analysis(img, spaces)
    cv2.imshow("Analisis Original (como main.py)", img_result)
    
    # Frame procesado (binario)
    img_processed = analyzer.get_processed_frame(img)
    cv2.imshow("Frame Procesado (binario)", img_processed)
    
    # Esperar tecla
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Estadísticas finales
    results = analyzer.analyze_spaces(img, spaces)
    occupied = sum(1 for r in results if r.is_occupied)
    free = len(results) - occupied
    
    print(f"\n📈 RESULTADOS FINALES (umbral 900):")
    print(f"   Total de espacios: {len(results)}")
    print(f"   Espacios ocupados: {occupied}")
    print(f"   Espacios libres: {free}")
    print(f"   Tasa de ocupación: {occupied/len(results)*100:.1f}%")
    
    print(f"\n✅ ¡El analizador que replica el código exitoso está funcionando!")

def test_with_video():
    """Prueba con video como el main.py original"""
    video_path = "assets/carPark.mp4"
    if not os.path.exists(video_path):
        print(f"⚠️  Video no encontrado: {video_path}")
        return
    
    print(f"\n🎥 Probando con video (como main.py original)...")
    
    # Cargar espacios
    spaces = load_spaces()
    if not spaces:
        return
    
    # Crear analizador con umbral original
    analyzer = WorkingOccupancyAnalyzer(pixel_threshold=900)
    
    # Abrir video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir el video: {video_path}")
        return
    
    print("📹 Reproduciendo video... Presiona 'q' para salir")
    
    frame_count = 0
    
    while True:
        # Loop del video como en main.py original
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        success, img = cap.read()
        if not success:
            break
        
        frame_count += 1
        
        # Análisis y visualización
        img_result = analyzer.visualize_analysis(img, spaces)
        
        # Mostrar frame número
        cv2.putText(img_result, f"Frame: {frame_count}", (10, img.shape[0] - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("Video Analysis (como main.py)", img_result)
        
        # Salir con 'q' (como original usa waitKey(10))
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Prueba de video completada")

if __name__ == "__main__":
    try:
        test_working_analyzer()
        
        # Preguntar si probar con video
        response = input("\n¿Quieres probar con el video? (y/n): ").lower().strip()
        if response == 'y':
            test_with_video()
            
    except KeyboardInterrupt:
        print("\n👋 Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()
