import os
from image_diet import settings
from django.conf import settings as main_settings
from django.contrib.staticfiles.storage import StaticFilesStorage


class ImageDietFileSystemStorage(StaticFilesStorage):

    def post_process(self, files, *args, **kwargs):
        results = []
        if settings.DIET_COMPRESS_STATIC_IMAGES:
            if 'image_diet' not in main_settings.INSTALLED_APPS:
                raise NotImplementedError("You need to install django_image_diet to use DIET_COMPRESS_STATIC_IMAGES")

            from image_diet.diet import squeeze
            for f in files:
                processed_file = squeeze(os.path.join(main_settings.STATIC_ROOT, f))
                results.append([f, processed_file, True if processed_file is not None else False])
        return results
