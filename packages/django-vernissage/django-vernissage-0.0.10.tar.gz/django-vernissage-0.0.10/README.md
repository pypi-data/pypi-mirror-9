# Vernissage

``django-vernissage`` is a reusable gallery app for django to be used
together with django-filer. It allows to create image galleries from
django-filer image files.

## Features

1. Defaults for easy usage with twitter bootstrap's carousels
2. Drag-and-drop ordering of the images in a gallery
3. Includes ready to use [django-cms](https://www.django-cms.org/en/) plugin

## Dependencies

Vernissage has been developed and tested with django 1.6. Usage with
1.7 should be pretty straightforward, but hasn't been tested yet.
You'll probably be asked to generate the new-style migrations, and
that should be it. If you want to do the migration work, please send a
pull request!

Vernissage uses
[django-admin-sortable2](http://django-admin-sortable2.readthedocs.org/)
to provide drag-and-drop sorting for the images in a gallery.

## Installation

1. Get it with pip:

   ```
   pip install django-vernissage
   ```

2. Add ``vernissage`` and ``adminsortable`` to ``INSTALLED_APPS``

   ```
   INSTALLED_APPS = (
	   ...
	   'vernissage',
	   'adminsortable',
	   ...
   )
   ```

3. run ``./manage.py syncdb`` (or ``./manage.py migrate`` if you're
   using ``south``.

If you want to use the django-cms plugin, it is possible that you
won't want the Vernissage models appearing in the admin. If so, set
the ``VERNISSAGE_ADMIN`` setting to ``False``

## Usage

Just go to the admin and create your galleries. You can sort the
images as you want them. An extremely basic template is provided, so
if you want to use your own (recommended), add your templates  to the
``VERNISSAGE_TEMPLATES`` setting:

```
VERNISSAGE_TEMPLATES = (
	("vernissage/carousel.html", "Carousel"),
	("vernissage/thumbnails.html", "Thumbnails and modal"),
)
```

## Versioning

The versioing is as follows: ``<major>.<minor>.<patch>``

Changes in ``patch`` are bugfixes. The expected functionality won't
change.

Changes in ``minor`` usually mean new features, but no
backwards-incompatible changes. Upgrade between minor versions might
require database migrations.

Changes in ``major`` include some API changes or changes that are for
some other reason backwards-incompatible or require some manual
intervention beyond just running ``migrate`` to upgrade from.

Finally, the first drafts versions will be labeled ``0.x.y`` until
such time when the websites this app has been originally developed for
finally get stabilized. Once we have something live, version ``1.0.0``
will be released whether that means backwards-incompatibility or not.
Until such time, we expect rapid development and API evolution, so if
you're using this before v1 please pay attention.
