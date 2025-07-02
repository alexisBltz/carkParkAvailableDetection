"""
Generador de iconos modernos para CarPark
Crea iconos SVG y convierte a ICO para la aplicación
"""
import os
from PIL import Image, ImageDraw, ImageFont
import io
import base64

def create_modern_icon():
    """Crea un icono moderno para la aplicación"""
    # Crear imagen 256x256 para alta resolución
    size = 256
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Colores modernos
    bg_color = (30, 30, 30)  # Fondo oscuro
    accent_color = (0, 120, 212)  # Azul moderno
    text_color = (255, 255, 255)  # Texto blanco
    
    # Dibujar fondo circular
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=bg_color, outline=accent_color, width=8)
    
    # Dibujar símbolo de carro simplificado
    car_width = size // 3
    car_height = size // 6
    car_x = (size - car_width) // 2
    car_y = (size - car_height) // 2 - 20
    
    # Cuerpo del carro
    draw.rectangle([car_x, car_y, car_x + car_width, car_y + car_height], 
                  fill=accent_color)
    
    # Ruedas
    wheel_size = car_height // 3
    wheel_y = car_y + car_height - wheel_size // 2
    
    # Rueda izquierda
    draw.ellipse([car_x + wheel_size, wheel_y, 
                 car_x + wheel_size + wheel_size, wheel_y + wheel_size], 
                fill=text_color)
    
    # Rueda derecha
    draw.ellipse([car_x + car_width - wheel_size*2, wheel_y, 
                 car_x + car_width - wheel_size, wheel_y + wheel_size], 
                fill=text_color)
    
    # Dibujar "P" de parking debajo
    try:
        # Intentar usar fuente del sistema
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        try:
            font = ImageFont.truetype("segoeui.ttf", 80)
        except:
            font = ImageFont.load_default()
    
    text = "P"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (size - text_width) // 2
    text_y = car_y + car_height + 30
    
    draw.text((text_x, text_y), text, fill=text_color, font=font)
    
    return image

def save_icon_formats(image, base_path="assets/icon"):
    """Guarda el icono en diferentes formatos"""
    # Crear directorio si no existe
    os.makedirs("assets", exist_ok=True)
    
    # Guardar como PNG de alta resolución
    image.save(f"{base_path}.png", "PNG")
    
    # Crear múltiples tamaños para ICO
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        resized = image.resize((size, size), Image.Resampling.LANCZOS)
        images.append(resized)
    
    # Guardar como ICO
    images[0].save(f"{base_path}.ico", format='ICO', sizes=[(img.width, img.height) for img in images])
    
    print(f"✅ Iconos guardados:")
    print(f"   📁 {base_path}.png")
    print(f"   📁 {base_path}.ico")

def create_app_icons():
    """Crea todos los iconos de la aplicación"""
    print("🎨 Generando iconos modernos para CarPark...")
    
    # Crear icono principal
    icon = create_modern_icon()
    save_icon_formats(icon)
    
    # Crear favicon para posible uso web
    favicon = icon.resize((32, 32), Image.Resampling.LANCZOS)
    favicon.save("assets/favicon.ico", "ICO")
    
    print("✅ Todos los iconos generados correctamente")

if __name__ == "__main__":
    create_app_icons()
