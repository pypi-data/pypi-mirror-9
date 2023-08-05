# -*- coding: utf-8 -*-
from __future__ import (absolute_import, unicode_literals)

import uuid
from django.utils.text import slugify

import os
from .models import StdImageField


class UploadTo(object):
    file_pattern = "%(name)s.%(ext)s"
    path_pattern = "%(path)s"

    def __call__(self, instance, filename):
        defaults = {
            'ext': filename.rsplit('.', 1)[1],
            'name': filename.rsplit('.', 1)[0],
            'path': filename.rsplit('/', 1)[0],
            'class_name': instance.__class__.__name__,
        }
        defaults.update(self.kwargs)
        return os.path.join(self.path_pattern % defaults,
                            self.file_pattern % defaults).lower()

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args

    def deconstruct(self):
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        return path, self.args, self.kwargs


class UploadToUUID(UploadTo):

    def __call__(self, instance, filename):
        self.kwargs.update({
            'name': uuid.uuid4().hex,
        })
        return super(UploadToUUID, self).__call__(instance, filename)


class UploadToClassNameDir(UploadTo):
    path_pattern = '%(class_name)s'


class UploadToClassNameDirUUID(UploadToClassNameDir, UploadToUUID):
    pass


class UploadToAutoSlug(UploadTo):

    def __init__(self, populate_from, **kwargs):
        self.populate_from = populate_from
        super(UploadToAutoSlug, self).__init__(populate_from, **kwargs)

    def __call__(self, instance, filename):
        field_value = getattr(instance, self.populate_from)
        self.kwargs.update({
            'name': slugify(field_value),
        })
        return super(UploadToAutoSlug, self).__call__(instance, filename)


class UploadToAutoSlugClassNameDir(UploadToClassNameDir, UploadToAutoSlug):
    pass


def pre_delete_delete_callback(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if isinstance(field, StdImageField):
            getattr(instance, field.name).delete()


def pre_save_delete_callback(sender, instance, **kwargs):
    if instance.pk:
        obj = sender.objects.get(pk=instance.pk)
        for field in instance._meta.fields:
            if isinstance(field, StdImageField):
                obj_field = getattr(obj, field.name)
                instance_field = getattr(instance, field.name)
                if obj_field and obj_field != instance_field:
                    obj_field.delete(False)
