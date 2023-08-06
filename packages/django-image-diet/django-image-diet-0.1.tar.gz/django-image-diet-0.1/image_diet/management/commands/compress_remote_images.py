import tempfile
import os
import time
import datetime
from optparse import make_option

from django.core.management.base import BaseCommand  # , CommandError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from basic_cms import settings as app_settings
import image_diet.settings as settings
from image_diet import squeeze


class Command(BaseCommand):
    help = "Compress images on external filesystem using image_diet. Creates a backup copy of compressed files"

    option_list = BaseCommand.option_list + (
        make_option(
            "--new_only",
            action='store_true',
            default=False,
            dest='new_only',
            help='Compress only new images',
        ),
        make_option(
            "--directory",
            action='append',
            type='string',
            default=[],
            dest='directories',
            help='Directory to compress. Options: all, path, default all. Recursive.'
        ),
    )

    def handle(self, new_only, directories, **options):
        if 'image_diet' not in app_settings.INSTALLED_APPS:
            raise NotImplementedError("You need to install image_diet to use this command")
        timestamp = time.time()
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('-%Y-%m-%d-%H:%M:%S')

        # todo:
        # add more options, like
        # directories - all, cms, directory list
        if not directories:
            directories.append('all')

        def process_file(path):
            """Process single file"""
            # failsafe copy of file
            copy = default_storage.open(path, 'rb')
            default_storage.save(path + timestamp, copy)
            copy.close()
            try:
                path = default_storage.path(path)
                squeeze(path, backup=False, flag_processed_file=False, new_only=False)
            except NotImplementedError:
                if path[-1:] != os.sep:
                    pf = default_storage.open(path, 'rwb')
                    image = pf.read()
                    tmpfilehandle, tmpfilepath = tempfile.mkstemp()
                    tmpfilehandle = os.fdopen(tmpfilehandle, 'wb')
                    tmpfilehandle.write(image)
                    tmpfilehandle.close()
                    squeeze(tmpfilepath)
                    tmpfilehandle = open(tmpfilepath)
                    pf.close()
                    default_storage.save(path, tmpfilehandle)
                    os.remove(tmpfilepath)

        def compress_files(directories, dirtree, new_only=False):
            compressed_flag = settings.DIET_FLAG_PROCESSED_FILE

            for f in directories[1]:  # files from listdir

                if f and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):  # sometimes if == [u'']
                    dir_path = os.sep.join(dirtree)
                    path = os.path.join(dir_path, f)
                    flagged_file_name = '.%s.%s' % (f, compressed_flag)
                    flag_path = os.path.join(dir_path, flagged_file_name)
                    print("Processing %s" % path)
                    if new_only:
                        should_process_file = False

                        if not default_storage.exists(flag_path):
                            should_process_file = True
                        else:
                            file_mt = default_storage.modified_time(path)
                            flag_mt = default_storage.modified_time(flag_path)
                            if flag_mt < file_mt:
                                should_process_file = True

                        if should_process_file:
                            process_file(path)
                    else:
                        process_file(path)

                    # add flag, for all files. This flag is used only when "new_only" option is called.
                    if default_storage.exists(flag_path):
                        default_storage.delete(flag_path)
                    default_storage.save(flag_path, ContentFile(""))

            for d in directories[0]:  # directories from list_dir
                dirtree.append(d)
                d = default_storage.listdir(os.sep.join(dirtree))
                compress_files(d, dirtree, new_only)
                dirtree.pop()  # remove last item, not needed anymore

        # proper start
        if 'all' in directories:
            directories = default_storage.listdir(os.path.sep)[0]

        for directory in directories:
            if directory:
                dirtree = [directory]
                d = default_storage.listdir(directory)
                compress_files(d, dirtree, new_only)
