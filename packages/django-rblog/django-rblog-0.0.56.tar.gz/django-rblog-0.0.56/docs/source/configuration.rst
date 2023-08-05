.. _configuration:

#############
Configuration
#############

If you're here I must asume you have the `django-rblog` installed in your own
Django_ based project. So let's play a bit with the configuration values.

*****************
Required settings
*****************

.. note::
    Theese are the minimum required settings to run django-rblog in a Django
    project

settings.INSTALLED_APPS
=======================
::

    INSTALLED_APPS += ('south',
                       'tinymce',
                       'filebrowser',
                       'tagging',
                       'sorl.thumbnail',
                       'disqus',
                       'compressor',
                       'rblog', )

Custom settings
===============
::

    # Disqus
    DISQUS_API_KEY = 'your-disqus-api-key'
    DISQUS_API_SECRET = 'your-disqus-api-secret'
    DISQUS_API_PUBLIC = 'your-disqus-api-public'
    DISQUS_WEBSITE_SHORTNAME = 'disqus-publicname'
    DISQUS_SYNC = True

    # Keys
    KEY_TLA = 'text-link-ads-key'
    KEY_BACKLINKS = 'backlinks-key'
    KEY_ANALYTICS = 'analytics-key'

    # Django_compressor
    COMPRESS_PRECOMPILERS = (
        ('text/coffeescript', 'coffee --compile --stdio'),
        ('text/less', 'lessc {infile} {outfile}'),
        ('text/x-sass', 'sass {infile} {outfile}'),
        ('text/x-scss', 'sass --scss {infile} {outfile}'),
        ('text/stylus', 'stylus < {infile} > {outfile}'),
    )
    COMPRESS_ENABLED = True
    COMPRESS_OUTPUT_DIR = 'cache'
    COMPRESS_ROOT = STATICFILES_DIRS[0]

Disqus
------

The comments can be integrated with Disqus_ and django-disqus_. You can go to
Disqus_ and register/login, then you have to create an app and we need to know
the keys to comunicate with::

    # Disqus
    DISQUS_API_KEY = 'your-disqus-api-key'
    DISQUS_API_SECRET = 'your-disqus-api-secret'
    DISQUS_API_PUBLIC = 'your-disqus-api-public'
    DISQUS_WEBSITE_SHORTNAME = 'disqus-publicname'
    DISQUS_SYNC = True

* **DISQUS_SYNC**: True if you want to sync the Disqus_ comments on
  `django-rblog`. There is a custom command to connect with Disqus_ and
  download the comments to the ``Comments`` table. If it's true you have to
  configure a cron executing the custom command and you will be able to write
  the comments directly on your html (SEO purposes).

Other keys
----------

By now we're supporting Analytics_, Backlinks_ and `Text Link Ads`_
(MatomySEO_), so you can configure that keys in ``settings.py`` and then call
it in templates::

    # Keys
    KEY_TLA = 'text-link-ads-key'
    KEY_BACKLINKS = 'backlinks-key'
    KEY_ANALYTICS = 'analytics-key'

.. note::
    Really you can add as many `keys` as you want because you have the control
    of templates. This ones are `oficially` supported but you can add your owns.
    If you want to oficially add more keys please see the
    :doc:`getting-involved` section.

Django-compressor
-----------------

If you want to server compressed and minified versions of the css/js files you
can do it just enabling the django-compressor_ settings::

    # Django_compressor
    COMPRESS_PRECOMPILERS = (
        ('text/coffeescript', 'coffee --compile --stdio'),
        ('text/less', 'lessc {infile} {outfile}'),
        ('text/x-sass', 'sass {infile} {outfile}'),
        ('text/x-scss', 'sass --scss {infile} {outfile}'),
        ('text/stylus', 'stylus < {infile} > {outfile}'),
    )
    COMPRESS_ENABLED = True
    COMPRESS_OUTPUT_DIR = 'cache'
    COMPRESS_ROOT = STATICFILES_DIRS[0]

It allows you to work with less, sass or stylus files. More information about
this in the django-compressor_ site.

.. _pip: http://www.pip-installer.org/en/latest/index.html
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _Django: http://djangoproject.org/
.. _Pygments: http://pygments.org/
.. _South: http://south.aeracode.org/
.. _PIL: http://www.pythonware.com/products/pil/
.. _django-tinymce: https://github.com/aljosa/django-tinymce
.. _django-tagging: https://code.google.com/p/django-tagging/
.. _sorl-thumbnail: http://sorl-thumbnail.readthedocs.org/en/latest/
.. _Disqus: http://disqus.com
.. _django-disqus: http://django-disqus.readthedocs.org/en/latest/
.. _django-compressor: https://github.com/django-compressor/django-compressor
.. _`Text Link Ads`: http://www.matomyseo.com/
.. _MatomySEO: http://www.matomyseo.com/
.. _Backlinks: http://backlinks.com/
.. _Analytics: http://www.google.com/analytics/