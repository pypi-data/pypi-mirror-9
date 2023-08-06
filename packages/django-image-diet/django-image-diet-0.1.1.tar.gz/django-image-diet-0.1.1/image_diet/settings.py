from django.conf import settings

DIET_DEBUG = getattr(settings, 'DIET_DEBUG', False)

DIET_JPEGOPTIM = getattr(settings, 'DIET_JPEGOPTIM', True)
DIET_JPEGTRAN = getattr(settings, 'DIET_JPEGTRAN', True)
DIET_GIFSICLE = getattr(settings, 'DIET_GIFSICLE', True)
DIET_OPTIPNG = getattr(settings, 'DIET_OPTIPNG', True)
DIET_ADVPNG = getattr(settings, 'DIET_ADVPNG', True)
DIET_PNGCRUSH = getattr(settings, 'DIET_PNGCRUSH', True)
DIET_PNGQUANT = getattr(settings, 'DIET_PNGQUANT', True)
DIET_PNGQUANT_BRUTE = getattr(settings, 'DIET_PNGQUANT_BRUTE', False)
DIET_IMAGE_BACKUPS = getattr(settings, 'DIET_IMAGE_BACKUPS', True)
DIET_COMPRESS_STATIC_IMAGES = getattr(settings, 'DIET_COMPRESS_STATIC_IMAGES', False)
DIET_COMPRESSED_FLAG = getattr(settings, 'DIET_COMPRESSED_FLAG', 'image_diet_compressed')
DIET_FLAG_PROCESSED_FILE = getattr(settings, 'DIET_FLAG_PROCESSED_FILE', True)
DIET_NEW_FILES_ONLY = getattr(settings, 'DIET_NEW_FILES_ONLY', True)
