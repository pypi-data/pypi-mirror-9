import logging
import time
import datetime
import os
from subprocess import call, PIPE
from imghdr import what as determinetype
from image_diet import settings

logger = logging.getLogger('image_diet')


def squeeze_jpeg():
    ''' Prefer jpegtran to jpegoptim since it makes smaller images
    and can create progressive jpegs (smaller and faster to load)'''
    if not settings.DIET_JPEGTRAN and not settings.DIET_JPEGOPTIM:  # Can't do anything
        return ""
    if not settings.DIET_JPEGTRAN:
        return u"jpegoptim -f --strip-all '%(file)s'"
    return (u"jpegtran -copy none -progressive -optimize -outfile '%(file)s'.diet '%(file)s' "
            "&& mv '%(file)s.diet' '%(file)s'")


def squeeze_gif():
    '''Gifsicle only optimizes animations.

    Eventually add support to change gifs to png8.'''
    return (u"gifsicle -O2 '%(file)s' > '%(file)s'.diet "
            "&& mv '%(file)s.diet' '%(file)s'") if settings.DIET_GIFSICLE else ""


def squeeze_png():
    commands = []
    if settings.DIET_OPTIPNG:
        commands.append(u"optipng -force -o7 '%(file)s'")
    if settings.DIET_ADVPNG:
        commands.append(u"advpng -z4 '%(file)s'")
    if settings.DIET_PNGCRUSH:
        commands.append(
            (u"pngcrush -rem gAMA -rem alla -rem cHRM -rem iCCP -rem sRGB "
             u"-rem time '%(file)s' '%(file)s.diet' "
             u"&& mv '%(file)s.diet' '%(file)s'")
        )
    if settings.DIET_PNGQUANT and not settings.DIET_PNGQUANT_BRUTE:
        commands.append(u"pngquant --force --verbose --quality 90-100 '%(file)s' -o '%(file)s' ")
    if settings.DIET_PNGQUANT_BRUTE:
        commands.append(u"pngquant --force --verbose '%(file)s' -o '%(file)s' ")
    return " && ".join(commands)


def backup_copy(path):
    if settings.DIET_IMAGE_BACKUPS:
        timestamp = time.time()
        timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d-%H:%M:%S')
        call("cp '%(file)s' '%(file)s-%(timestamp)s'" % {'file': path, 'timestamp': timestamp},
             shell=True, stdout=PIPE)


def get_flag_path(path):
    filename = os.path.basename(path)
    directory = os.path.split(path)[0]
    flagged_file_name = '.%s.%s' % (filename, settings.DIET_COMPRESSED_FLAG)
    flag_path = os.path.join(directory, flagged_file_name)
    return flag_path


def create_processed_file_flag(path):
    flag_path = get_flag_path(path)
    call("touch '%s'" % flag_path, shell=True)


def squeeze(path, backup=settings.DIET_IMAGE_BACKUPS, flag_processed_file=settings.DIET_FLAG_PROCESSED_FILE,
            new_only=settings.DIET_NEW_FILES_ONLY):
    '''Returns path of optimized image or None if something went wrong.'''
    if not os.path.exists(path):
        logger.error("'%s' does not point to a file." % path)
        return None

    filetype = determinetype(path)

    if backup:
        backup_copy(path)

    squeeze_cmd = ""
    if filetype == "jpeg":
        squeeze_cmd = squeeze_jpeg()
    elif filetype == "gif":
        squeeze_cmd = squeeze_gif()
    elif filetype == "png":
        squeeze_cmd = squeeze_png()

    if new_only:
        should_process_file = False
        flag_path = get_flag_path(path)
        flag_path = get_flag_path(path)

        if not os.path.exists(flag_path):
            should_process_file = True
        else:
            file_mt = os.path.getmtime(path)
            flag_mt = os.path.getmtime(flag_path)

            if flag_mt < file_mt:
                should_process_file = True

        if not should_process_file:
            squeeze_cmd = False

    if squeeze_cmd:
        try:
            retcode = call(squeeze_cmd % {'file': path},
                           shell=True, stdout=PIPE)
            if flag_processed_file:
                create_processed_file_flag(path)
        except:
            raise
            logger.error('Squeezing failed with parameters:')
            logger.error(squeeze_cmd[filetype] % {'file': path})
            logger.exception()
            return None

        if retcode != 0:
            # Failed.
            logger.error(
                ('Squeezing failed. '
                 'Likely because you are missing one of required utilities.'))
            return None
    return path
