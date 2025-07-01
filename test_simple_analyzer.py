#!/usr/bin/env python3
"""
Prueba del analizador simple - basado en el código eficaz de ParkingSpacePicker
"""
import cv2
import numpy as np
import pickle
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.simple_analyzer import SimpleOccupancyAnalyzer
from src.models import ParkingSpace

def load_spaces_from_carpark_pos():
    """Carga espacios desde el archivo CarParkPos (formato pickle)"""
    width, height = 107, 48  # Tamaño estándar de los espacios
    
    try:
        with open('assets/CarParkPos', 'rb') as f:
            pos_list = pickle.load(f)
        
        spaces = []
        for i, (x, y) in enumerate(pos_list):
            space = ParkingSpace(
                id=f"space_{i}",
                x=x,
                y=y,
                width=width,
                height=height
            )
            spaces.append(space)
        
        print(f"✅ Cargados {len(spaces)} espacios desde CarParkPos")
        return spaces
        
    except FileNotFoundError:
        print("❌ No se encontró el archivo CarParkPos")
        return []
    except Exception as e:
        print(f"❌ Error cargando espacios: {e}")
        return []

def test_simple_analyzer():
    """Prueba el analizador simple con imagen estática"""
    print("🚗 Prueba del Analizador Simple")
    print("=" * 40)
    
    # Cargar imagen
    image_path = "assets/carParkImg.png"
    if not os.path.exists(image_path):
        print(f"❌ No se encontró la imagen: {image_path}")
        return
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ No se pudo cargar la imagen: {image_path}")
        return
    
    print(f"✅ Imagen cargada: {img.shape}")
    
    # Cargar espacios
    spaces = load_spaces_from_carpark_pos()
    if not spaces:
        print("❌ No hay espacios definidos")
        return
    
    # Crear analizador con diferentes umbrales
    thresholds = [0.2, 0.23, 0.25, 0.3]
    
    for threshold in thresholds:
        print(f"\n📊 Analizando con umbral: {threshold}")
        analyzer = SimpleOccupancyAnalyzer(threshold=threshold)
        
        # Análisis básico
        results_basic = analyzer.analyze_spaces(img, spaces)
        occupied_basic = sum(1 for r in results_basic if r.is_occupied)
        free_basic = len(results_basic) - occupied_basic
        
        # Análisis con preprocesamiento
        results_enhanced = analyzer.analyze_with_preprocessing(img, spaces)
        occupied_enhanced = sum(1 for r in results_enhanced if r.is_occupied)
        free_enhanced = len(results_enhanced) - occupied_enhanced
        
        print(f"   Básico:     {occupied_basic} ocupados, {free_basic} libres")
        print(f"   Mejorado:   {occupied_enhanced} ocupados, {free_enhanced} libres")
        
        # Crear visualización
        img_visual = img.copy()
        
        # Dibujar espacios con resultados
        for i, (space, result) in enumerate(zip(spaces, results_enhanced)):
            color = (0, 0, 255) if result.is_occupied else (0, 255, 0)  # Rojo = ocupado, Verde = libre
            
            # Dibujar rectángulo
            cv2.rectangle(img_visual, 
                         (space.x, space.y), 
                         (space.x + space.width, space.y + space.height), 
                         color, 2)
            
            # Dibujar índice del espacio
            cv2.putText(img_visual, str(i), 
                       (space.x + 5, space.y + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Dibujar confianza si es alta
            if result.confidence > 0.5:
                conf_text = f"{result.confidence:.2f}"
                cv2.putText(img_visual, conf_text, 
                           (space.x + 5, space.y + space.height - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        # Dibujar estadísticas
        stats_text = f"Threshold: {threshold} | Ocupados: {occupied_enhanced} | Libres: {free_enhanced}"
        cv2.putText(img_visual, stats_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Mostrar resultado
        window_name = f"Analisis Simple - Threshold {threshold}"
        cv2.imshow(window_name, img_visual)
        
        # Esperar tecla
        print(f"   👀 Presiona cualquier tecla para continuar (ventana: {window_name})")
        cv2.waitKey(0)
        cv2.destroyWindow(window_name)
    
    # Análisis detallado de algunos espacios
    print(f"\n🔍 Análisis detallado de los primeros 5 espacios:")
    analyzer = SimpleOccupancyAnalyzer(threshold=0.23)  # Umbral óptimo típico
    
    for i in range(min(5, len(spaces))):
        space = spaces[i]
        debug_info = analyzer.debug_space_analysis(img, space)
        
        print(f"\n   Espacio {i}:")
        print(f"     Posición: ({space.x}, {space.y}) - {space.width}x{space.height}")
        print(f"     Intensidad media: {debug_info.get('mean_intensity', 0):.1f}")
        print(f"     Intensidad normalizada: {debug_info.get('normalized_intensity', 0):.3f}")
        print(f"     Umbral: {debug_info.get('threshold', 0):.3f}")
        print(f"     Estado: {'🚗 OCUPADO' if debug_info.get('is_occupied', False) else '⭕ LIBRE'}")
    
    print(f"\n✅ Prueba completada. El analizador simple está funcionando!")

def test_with_video():
    """Prueba el analizador con video (si está disponible)"""
    video_path = "assets/carPark.mp4"
    if not os.path.exists(video_path):
        print(f"⚠️  Video no encontrado: {video_path}")
        return
    
    print(f"\n🎥 Probando con video...")
    
    # Cargar espacios
    spaces = load_spaces_from_carpark_pos()
    if not spaces:
        return
    
    # Crear analizador
    analyzer = SimpleOccupancyAnalyzer(threshold=0.23)
    
    # Abrir video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ No se pudo abrir el video: {video_path}")
        return
    
    frame_count = 0
    print("📹 Reproduciendo video... Presiona 'q' para salir")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Analizar cada 10 frames para mejor rendimiento
        if frame_count % 10 == 0:
            results = analyzer.analyze_spaces(frame, spaces)
            
            # Dibujar resultados
            for space, result in zip(spaces, results):
                color = (0, 0, 255) if result.is_occupied else (0, 255, 0)
                cv2.rectangle(frame, 
                             (space.x, space.y), 
                             (space.x + space.width, space.y + space.height), 
                             color, 2)
            
            # Estadísticas
            occupied = sum(1 for r in results if r.is_occupied)
            free = len(results) - occupied
            stats_text = f"Frame: {frame_count} | Ocupados: {occupied} | Libres: {free}"
            cv2.putText(frame, stats_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow("Video Analysis", frame)
        
        # Salir con 'q'
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Prueba de video completada")

if __name__ == "__main__":
    try:
        test_simple_analyzer()
        
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
