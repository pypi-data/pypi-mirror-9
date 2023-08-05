============
Django Diazo
============

Integrate Diazo in Django using WSGI middleware and add/change themes
using the Django Admin interface.

The code is maintained on GitHub (https://github.com/Goldmund-Wyldebeast-Wunderliebe/django-diazo).


------------
Installation
------------

Install the package::

    pip install django-diazo

~~~~~~~~~~~~
settings.py
~~~~~~~~~~~~

Add the app to your project::

    INSTALLED_APPS = (
        ...
        'adminsortable',
        'django_diazo',
        ...
    )

Add middleware (or WSGI, see below)::

    MIDDLEWARE_CLASSES += (
        'django_diazo.middleware.DjangoDiazoMiddleware',
        'django_diazo.contrib.cms.middleware.DjangoCmsDiazoMiddleware',  # Toolbar on/off switch, if you use Django CMS 3
    )

If you want to know if Django-Diazo is turned on in your templates add::

    TEMPLATE_CONTEXT_PROCESSORS = (
        ...
        'django_diazo.context_processors.diazo_enabled',
    )

The variable ``DIAZO_ENABLED`` is now available in your templates.

!! IMPORTANT !!
Note that when using the Django middleware instrumentation the Diazo ``<notheme />`` rules won't work.
You have to provide regular expression patterns in ``Theme.pattern`` to prevent some pages (by url) to be themed.
When you want to disable theming for certain pages by content based rules for ``<notheme />``, you need to use the
WSGI middleware instead.

~~~~~~~
wsgi.py
~~~~~~~

If you rather use WSGI than Django middleware or you have to (at the moment) since you use exotic ``<notheme />`` rules,
add the following lines to your ``wsgi.py`` file::

    # Apply WSGI middleware here.
    from django_diazo.wsgi import DiazoMiddlewareWrapper
    application = DiazoMiddlewareWrapper(application)

~~~~~~~~~~~~~~~~~~~~~~~~~~~
Database (South migrations)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Migrate the database::

    python manage.py migrate django_diazo


-----------------------
Create a built-in theme
-----------------------

You might want to supply your Django application with an out-of-the-box
theme, probably also managed in a VCS.

Create a new app with a ``diazo.py`` file in its root. The contents of
this file is should be something like this::

    from django_diazo.theme import DiazoTheme, registry

    class SomeTheme(DiazoTheme):
        name = 'Some Theme'
        slug = 'some_theme'
        pattern = '^(?!.*admin)'  # Theme everything but /admin
    registry.register(SomeTheme)

Don't forget to put your assets in the static folder, like an ``index.html`` and a ``rules.xml``. You can find a
``rules.xml`` example in ``django_diazo/examples``.

To synchronize the built-in themes with the database/application run the
following command::

    python manage.py syncthemes


-------------
Upload themes
-------------

By default, the .zip files that are uploaded are extracted in the media
folder. You might want to serve these files via Django. Add the
following to your ``urls.py``::

    urlpatterns += patterns('',
        ...
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        ...
    )

For production environments it is not recommended to serve files from
the media folder. This implementation only servers files in the
``themes`` folder within the media folder but it would be better to
serve these files using a web server and not via Django.
The same holds for your ``static`` folder.


----------------------------
Example themes / application
----------------------------

Take a look at https://github.com/Goldmund-Wyldebeast-Wunderliebe/django-diazo-themes and
https://github.com/Goldmund-Wyldebeast-Wunderliebe/django-diazo-blog for examples of built-in themes and an integration
example.

Our blog post http://www.goldmund-wyldebeast-wunderliebe.com/tech-blog/blog-posts/using-diazo-in-django also covers
these examples and some more background.
