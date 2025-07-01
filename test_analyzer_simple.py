#!/usr/bin/env python3
"""
Prueba Simple del Analizador - Sin ventanas gráficas
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

def load_spaces():
    """Carga espacios desde CarParkPos"""
    width, height = 107, 48
    
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

def test_analyzer():
    """Prueba básica del analizador"""
    print("🚗 Prueba del Analizador Simple (Sin ventanas)")
    print("=" * 50)
    
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
    
    # Probar diferentes umbrales
    thresholds = [0.15, 0.20, 0.23, 0.25, 0.30, 0.35]
    
    print(f"\n📊 Resultados por umbral:")
    print("Umbral | Ocupados | Libres | Ratio")
    print("-" * 35)
    
    for threshold in thresholds:
        analyzer = SimpleOccupancyAnalyzer(threshold=threshold)
        results = analyzer.analyze_spaces(img, spaces)
        
        occupied = sum(1 for r in results if r.is_occupied)
        free = len(results) - occupied
        ratio = occupied / len(results) * 100
        
        print(f"{threshold:6.2f} | {occupied:8d} | {free:6d} | {ratio:5.1f}%")
    
    # Análisis detallado de algunos espacios
    print(f"\n🔍 Análisis detallado (umbral 0.23):")
    analyzer = SimpleOccupancyAnalyzer(threshold=0.23)
    
    # Analizar primeros 10 espacios
    for i in range(min(10, len(spaces))):
        space = spaces[i]
        debug_info = analyzer.debug_space_analysis(img, space)
        
        intensity = debug_info.get('normalized_intensity', 0)
        is_occupied = debug_info.get('is_occupied', False)
        status = "🚗 OCUPADO" if is_occupied else "⭕ LIBRE"
        
        print(f"Espacio {i:2d}: Intensidad={intensity:.3f} -> {status}")
    
    # Buscar umbral óptimo
    print(f"\n🎯 Buscando umbral óptimo...")
    
    # Analizar distribución de intensidades
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    intensities = []
    
    for space in spaces:
        roi = gray[space.y:space.y + space.height, space.x:space.x + space.width]
        if roi.size > 0:
            mean_intensity = float(np.mean(roi)) / 255.0
            intensities.append(mean_intensity)
    
    if intensities:
        intensities = np.array(intensities)
        mean_all = np.mean(intensities)
        std_all = np.std(intensities)
        min_intensity = np.min(intensities)
        max_intensity = np.max(intensities)
        
        print(f"Estadísticas de intensidades:")
        print(f"  Media: {mean_all:.3f}")
        print(f"  Desviación: {std_all:.3f}")
        print(f"  Mínimo: {min_intensity:.3f}")
        print(f"  Máximo: {max_intensity:.3f}")
        
        # Sugerir umbral
        suggested_threshold = float(mean_all - (std_all * 0.5))
        print(f"  Umbral sugerido: {suggested_threshold:.3f}")
        
        # Probar umbral sugerido
        analyzer.set_threshold(suggested_threshold)
        results = analyzer.analyze_spaces(img, spaces)
        occupied = sum(1 for r in results if r.is_occupied)
        print(f"  Con umbral sugerido: {occupied} ocupados de {len(spaces)}")
    
    print(f"\n✅ Análisis completado!")

if __name__ == "__main__":
    try:
        test_analyzer()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
