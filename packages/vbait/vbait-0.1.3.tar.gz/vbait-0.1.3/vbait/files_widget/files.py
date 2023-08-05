# coding=utf-8
import os
from io import FileIO, BufferedWriter
import re
import time

from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify
import shutil

from conf import *


def filename_from_path(path):
    return re.sub(r'^.+/', '', path)


def model_slug(model):
    return slugify(model._meta.verbose_name_plural)


def construct_temp_path(user):
    now = time.localtime()[0:5]
    dir_name = TEMP_DIR_FORMAT % now
    return os.path.join(TEMP_DIR, dir_name, str(user.pk)).replace('\\', '/')


def construct_permanent_path(instance, field):
    model_dir = model_slug(type(instance))
    return os.path.join(getattr(instance, field.name).upload_to(), str(instance.pk)).replace('\\', '/')


def in_directory(path, directory):
    # don't try to manipulate with ../../
    full_path = os.path.join(MEDIA_ROOT, path)
    return path.startswith(directory) and full_path == os.path.realpath(full_path).replace('\\', '/')


def in_permanent_directory(path, instance, field):
    full_path = os.path.join(MEDIA_ROOT, path)
    return path.startswith(construct_permanent_path(instance, field)) and \
           full_path == os.path.realpath(full_path).replace('\\', '/')


def make_temp_directory(filename, user):
    public_dir = construct_temp_path(user)
    full_dir = os.path.join(settings.MEDIA_ROOT, public_dir)

    try:
        if not os.path.exists(full_dir):
            os.makedirs(full_dir)
    except EnvironmentError:
        # deepest dir already exists
        pass

    full_path = os.path.join(full_dir, filename).replace('\\', '/')
    available_full_path = default_storage.get_available_name(full_path)
    return available_full_path


def make_permanent_directory(temp_path, instance, field):
    public_dir = construct_permanent_path(instance, field)
    filename = filename_from_path(temp_path)
    full_dir = os.path.join(MEDIA_ROOT, public_dir)

    if not os.path.exists(full_dir):
        os.makedirs(full_dir)

    full_path = os.path.join(full_dir, filename).replace('\\', '/')
    available_full_path = default_storage.get_available_name(full_path)
    return available_full_path


def save_upload(uploaded, filename, raw_data, user):
    '''
    raw_data: if True, uploaded is an HttpRequest object with the file being
    the raw post data
    if False, uploaded has been submitted via the basic form
    submission and is a regular Django UploadedFile in request.FILES
    '''

    path = make_temp_directory(filename, user)
    public_path = path.replace(MEDIA_ROOT, '', 1)

    # try:
    with BufferedWriter(FileIO(path, "wb")) as dest:
        # if the "advanced" upload, read directly from the HTTP request
        # with the Django 1.3 functionality
        if raw_data:
            foo = uploaded.read(1024)
            while foo:
                dest.write(foo)
                foo = uploaded.read(1024)
        # if not raw, it was a form upload so read in the normal Django chunks fashion
        else:
            for c in uploaded.chunks():
                dest.write(c)
        # got through saving the upload, report success
        return public_path
        # except IOError:
        # could not open the file most likely
    # pass
    return False


def try_to_recover_path(temp_path, instance, field):
    filename = filename_from_path(temp_path)
    permanent_directory = construct_permanent_path(instance, field)
    permanent_path = os.path.join(permanent_directory, filename).replace('\\', '/')
    full_path = os.path.join(MEDIA_ROOT, permanent_path).replace('\\', '/')
    if os.path.exists(full_path):
        return permanent_path, True
    else:
        return temp_path, False


def move_to_permanent_directory(temp_path, instance, field):
    if temp_path.startswith('/') or temp_path.find('//') != -1 \
            or in_permanent_directory(temp_path, instance, field):
        return temp_path, False

    full_path = make_permanent_directory(temp_path, instance, field)
    public_path = full_path.replace(MEDIA_ROOT, '', 1)
    full_temp_path = os.path.join(MEDIA_ROOT, temp_path)
    try:
        shutil.move(full_temp_path, full_path)
    except EnvironmentError:
        return try_to_recover_path(temp_path, instance, field)

    return public_path, True


def manage_files_on_disk(sender, instance, **kwargs):
    # Receiver of Django post_save signal.
    # At this point we know that the model instance has been saved into the db.
    from fields import ImagesField, ImageField

    fields = [field for field in sender._meta.fields if type(field) in [ImagesField, ImageField]]

    for field in fields:
        old_value_attr = OLD_VALUE_STR % field.name
        deleted_value_attr = DELETED_VALUE_STR % field.name
        moved_value_attr = MOVED_VALUE_STR % field.name
        prime_value_attr = PRIME_VALUE_STR % field.name
        if not hasattr(instance, old_value_attr):
            continue

        old_images = (getattr(instance, old_value_attr) or '').splitlines()
        current_images = (getattr(instance, field.name) or '').splitlines()
        deleted_images = (getattr(instance, deleted_value_attr) or '').splitlines()
        moved_images = (getattr(instance, moved_value_attr) or '').splitlines()
        prime_image = (getattr(instance, prime_value_attr, None) or '')
        new_images = []
        changed = False

        # Delete removed images from disk if they are in our FILES_DIR.
        # we implement redundant checks to be absolutely sure that
        # files must be deleted. For example, if a JS error leads to
        # incorrect file lists in the hidden inputs, we reconstruct the old value.
        #
        # O = old_images, C = current_images, D = deleted_images
        #
        # what do we do with files that appear in:
        #
        # ---  (OK)    do nothing, we don't even know it's name :)
        # --D  (OK)    if in temp dir or permanent dir of inst: delete from disk
        # -C-  (OK)    if not in permanent dir of inst, create hard link if possible;
        # if in temp dir, delete
        # -CD  (ERROR) show warning message after save
        #   O--  (ERROR) put back in current, show warning message after save
        #   O-D  (OK)    if in temp dir or permanent dir of inst: delete from disk
        #   OC-  (OK)    if not in permanent dir of inst, create hard link if possible;
        #                if in temp dir, delete
        #   OCD  (ERROR) show warning message after save

        for img in current_images:
            # OC-, -C-, OCD & -CD
            file_path, file_name = decompress_value(img)
            if in_directory(file_path, TEMP_DIR) or in_directory(file_path, getattr(instance, field.name).upload_to()):
                new_path, path_changed = move_to_permanent_directory(file_path, instance, field)
                if prime_image and prime_image == file_path:
                    prime_image = new_path
                if path_changed:
                    changed = True
                new_images.append(compress_params(new_path, file_name))

        for img in deleted_images:
            new_path, file_name = decompress_value(img)
            if img not in current_images:
                # --D & O-D
                if in_permanent_directory(new_path, instance, field) or in_directory(new_path, TEMP_DIR):
                    try:
                        os.remove(os.path.join(MEDIA_ROOT, new_path))
                    except EnvironmentError as e:
                        pass

        for img in old_images:
            new_path, file_name = decompress_value(img)
            if not path_in_list_images(new_path, current_images) and \
                    not path_in_list_images(new_path, deleted_images) and \
                    not path_in_list_images(new_path, moved_images):
                # O--
                changed = True
                new_images.append(img)
                #if img not in current_images and img not in deleted_images and img not in moved_images:
                # O--
                #    changed = True
                #    new_images.append(img)

        delattr(instance, old_value_attr)
        delattr(instance, deleted_value_attr)
        delattr(instance, moved_value_attr)
        if hasattr(instance, prime_value_attr):
            delattr(instance, prime_value_attr)
        if changed or prime_image:
            new_images = check_prime_img(prime_image, new_images, instance)
            setattr(instance, field.name, '\n'.join(new_images))
            instance.save()


def decompress_value(value):
    try:
        path_to_file, name, is_prime = value.split('||')
    except ValueError:
        path_to_file, name = value.split('||')
        is_prime = None
    return path_to_file.replace('\\', '/'), name


def compress_params(path_to_file, name, is_prime=None):
    if is_prime:
        return "%s||%s||%s" % (path_to_file, name, is_prime)
    return "%s||%s" % (path_to_file, name)


def path_in_list_images(path, images):
    for img in images:
        img_path, img_name = decompress_value(img)
        if path == img_path:
            return True
    return False


def check_prime_img(prime_image, images, instance):
    new_images = []
    for img in images:
        img_path, img_name = decompress_value(img)
        if prime_image == img_path:
            new_images.append(compress_params(img_path, img_name, "prime"))
        else:
            new_images.append(compress_params(img_path, img_name))
    return new_images
