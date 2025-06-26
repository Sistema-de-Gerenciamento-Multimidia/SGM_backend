from PIL import Image
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import IFDRational


def extract_image_info(image_path):
    image = Image.open(image_path)
    
    # Dimensões
    width, height = image.size
    
    # Profundidade de Cor
    color_depth = image.mode
    
    # Resolução (DPI)
    dpi = image.info.get('dpi', None)
    resolution = f"{dpi[0]}x{dpi[1]}" if dpi and len(dpi) == 2 and isinstance(dpi, tuple) else None
    
    # Extrai dados EXIF da imagem
    exif_data = image.getexif()
    exif = {}
    
    if exif_data:
        # Itera sobre todos os ids dos dados exif
        for tag_id, data in exif_data.items():
            if isinstance(data, IFDRational):
                data = float(data)
            # Retorna o nome da tag a partir do tag_id
            if tag_id in TAGS:
                exif[TAGS[tag_id]] = data
            else:
                exif[tag_id] = data
    
    extracted_data = {
        "Dimensions": f"{width}x{height}",
        "ColorDepth": color_depth,
        "DPI": resolution,
        "Exif": exif
    }
    
    return extracted_data
