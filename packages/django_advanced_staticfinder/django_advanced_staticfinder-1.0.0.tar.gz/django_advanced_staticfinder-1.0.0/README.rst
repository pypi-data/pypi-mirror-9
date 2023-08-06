django_advanced_staticfinder
============

Custom filesystem finder for Django static files allowing ignore rules to be configured in settings

To use in in your django project, it needs to be installed:

::

    $ pip install django_advanced_staticfinder

And ``"advanced_staticfinder"`` needs to be in your ``settings.INSTALLED_APPS``.

Then you can configure ignore rules like so:

::

    STATICFILES_FINDERS_IGNORE = [
        '*.scss',
        '*.js',
    ]

Changes
-------

1.0.0 - Initial release for PyPI
