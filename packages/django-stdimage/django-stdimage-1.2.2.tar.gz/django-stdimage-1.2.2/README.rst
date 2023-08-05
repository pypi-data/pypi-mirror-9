.. image:: https://travis-ci.org/codingjoe/django-stdimage.png?branch=master
    :target: https://travis-ci.org/codingjoe/django-stdimage

.. image:: https://coveralls.io/repos/codingjoe/django-stdimage/badge.png?branch=master
    :target: https://coveralls.io/r/codingjoe/django-stdimage

.. image:: https://scrutinizer-ci.com/g/codingjoe/django-stdimage/badges/quality-score.png?b=master
    :target: https://scrutinizer-ci.com/g/codingjoe/django-stdimage/?branch=master

.. image:: https://pypip.in/v/django-stdimage/badge.png
    :target: https://crate.io/packages/django-stdimage

.. image:: https://pypip.in/status/django-stdimage/badge.svg
    :target: https://pypi.python.org/pypi/django-stdimage/
    :alt: Development Status

.. image:: https://pypip.in/py_versions/django-stdimage/badge.svg
    :target: https://pypi.python.org/pypi/django-stdimage/
    :alt: Supported Python versions

.. image:: https://pypip.in/d/django-stdimage/badge.png
    :target: https://crate.io/packages/django-stdimage/
    :alt: Downloads

.. image:: https://pypip.in/license/django-stdimage/badge.png
    :target: https://pypi.python.org/pypi/django-stdimage/
    :alt: License

Django Standarized Image Field
==============================

Django Field that implement the following features:

* Django-Storages compatible (S3)
* Python 2, 3 and PyPy support
* Django 1.5 and later support
* Resize images to different sizes
* Access thumbnails on model level, no template tags required
* Preserves original image
* Restrict accepted image dimensions
* Rename files to a standardized name (using a callable upload_to)

Installation
------------

Simply install the latest stable package using the command

``easy_install django-stdimage`` or ``pip django-stdimage``

and add ``'stdimage'`` to ``INSTALLED_APPs`` in your settings.py, that's it!

Usage
-----

``StdImageField`` works just like Django's own `ImageField <https://docs.djangoproject.com/en/dev/ref/models/fields/#imagefield>`_ except that you can specify different sized variations.

Variations
 Variations are specified withing a dictionary. The key will will be the attribute referencing the resized image.
 A variation can be defined both as a tuple or a dictionary.

 Example::

     from stdimage.models import StdImageField

     class MyModel(models.Model):
         # works just like django's ImageField
         image = StdImageField(upload_to='path/to/img')

         # creates a thumbnail resized to maximum size to fit a 100x75 area
         image = StdImageField(upload_to='path/to/img', variations={'thumbnail': {'with': 100, 'height': 75}})

         # is the same as dictionary-style call
         image = StdImageField(upload_to='path/to/img', variations={'thumbnail': (100, 75)})

         # creates a thumbnail resized to 100x100 croping if necessary
         image = StdImageField(upload_to='path/to/img', variations={
            'thumbnail': {"width": 100, "height": 100, "crop":True}
         })

         ## Full ammo here. Please note all the definitions below are equal
         image = StdImageField(upload_to=upload_to, blank=True, variations={
             'large': (600, 400),
             'thumbnail': (100, 100, True),
             'medium': (300, 200),
         })

 For using generated variations in templates use "myimagefield.variation_name".
 
 Example::

     <a href="{{ object.myimage.url }}"><img alt="" src="{{ object.myimage.thumbnail.url }}"/></a>


Utils
 By default StdImageField stores images without modifying the file name.
 If you want to use more consistent file names you can use the build in upload callables.
 
 Example::

     from stdimage.utils import UploadToUUID, UploadToClassNameDir, UploadToAutoSlug, UploadToAutoSlugClassNameDir

     class MyClass(models.Model)
         # Gets saved to MEDIA_ROOT/myclass/#FILENAME#.#EXT#
         image1 = StdImageField(upload_to=UploadToClassNameDir())
 
         # Gets saved to MEDIA_ROOT/myclass/pic.#EXT#
         image2 = StdImageField(upload_to=UploadToClassNameDir(name='pic'))

         # Gets saved to MEDIA_ROOT/images/#UUID#.#EXT#
         image3 = StdImageField(upload_to=UploadToUUID(path='images'))

         # Gets saved to MEDIA_ROOT/myclass/#UUID#.#EXT#
         image4 = StdImageField(upload_to=UploadToClassNameDirUUID())

         # Gets save to MEDIA_ROOT/images/#SLUG#.#EXT#
         image5 = StdImageField(upload_to=UploadToAutoSlug(path='images))

         # Gets save to MEDIA_ROOT/myclass/#SLUG#.#EXT#
         image6 = StdImageField(upload_to=UploadToAutoSlugClassNameDir())

Validators
 The `StdImageField` doesn't implement any size validation. Validation can be specified using the validator attribute
 and using a set of validators shipped with this package.
 Validators can be used for both Forms and Models.

 Example::

    from stdimage.validators import UploadToUUID, UploadToClassNameDir, UploadToAutoSlug, UploadToAutoSlugClassNameDir

    class MyClass(models.Model)
        image1 = StdImageField(validators=MinSizeValidator(800, 600))
        image2 = StdImageField(validators=MaxSizeValidator(1028, 768))

 CAUTION: The MaxSizeValidator should be used with caution.
 As storage isn't expensive, you shouldn't restrict upload dimensions.
 If you seek prevent users form overflowing your memory you should restrict the HTTP upload body size.

Deleting images
 Django `dropped support
 <https://docs.djangoproject.com/en/dev/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files>`_. for automated deletions in version 1.3.
 Implementing file deletion `should be done
 <http://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab>`_. inside your own applications using the `post_delete` or `pre_delete` signal.
 Clearing the field if blank is true, does not delete the file. This can also be achieved using `pre_save` and `post_save` signals.
 This packages contains two signal callback methods that handle file deletion for all SdtImageFields of a model.::

    from stdimage import pre_delete_delete_callback, pre_save_delete_callback

    post_delete.connect(pre_delete_delete_callback, sender=MyModel)
    pre_save.connect(pre_save_delete_callback, sender=MyModel)


 Warning: You should not use the singal callbacks in production. They may result in data loss.


Re-rendering variations
 You might want to add new variations to a field. That means you need to render new variations for missing fields.
 This can be accomplished using a management command.::

    python manage.py rendervariations 'app_name.model_name.field_name' [--replace]

 The `replace` option will replace all existing files.
 There is currently a memory leak, that's why you should avoid using the `replace` option in cron jobs.


Testing
-------
To run the tests simply run ``python setup.py test``
