.. _advanced:

########
Advanced
########

Commands
********

This `django-rblog` has some extra management commands. Here is where we have
to write the documentation about the commands.

disqus_comments
---------------

This command connects with Disqus_ and downloads (vía Disqus API) the comments
to the `django-rblog` database. The main goal of this command is:

* To have a full backup with all the comments.
* To be able to show them in html (SEO purposes).

We can get synced with the comments just running this command manually or making
it runs as a cron tab::

    $ ./manage.py disqus_comments
    $ crontab -l
    */55 * * * * cd /path/yourblog/ ; source env/bin/activate ; cd src ; python manage.py disqus_comments > /dev/null


Templatetags
************

There are some custom templatetags to help a bit with the template creation.

tla.py
------

This templatetag displays the links powered by `Text Link Ads`_ platform (called
now MatomySEO_). Requires a settings configuration and a template to run. We
have already seen the configuration value::

    KEY_TLA = 'text-link-ads-key'

The call to this templatetag (in a template) is going to be like that::

    {% load tla %}
    ...
    {% tla_list %}

backlinks.py
------------

This templatetag displays the links powered by Backlinks_ platform. Requires a
settings configuration and a template to run. We have already seen the
configuration value::

    KEY_BACKLINKS = 'backlinks-key'

The call to this templatetag (in a template) is going to be like that::

    {% load backlinks %}
    ...
    {{ backlinks_list }}



.. _pip: http://www.pip-installer.org/en/latest/index.html
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _Django: http://djangoproject.org/
.. _Pygments: http://pygments.org/
.. _South: http://south.aeracode.org/
.. _PIL: http://www.pythonware.com/products/pil/
.. _django-tinymce: https://github.com/aljosa/django-tinymce
.. _django-tagging: https://code.google.com/p/django-tagging/
.. _sorl-thumbnail: http://sorl-thumbnail.readthedocs.org/en/latest/
.. _django-compressor: https://github.com/django-compressor/django-compressor
.. _Disqus: http://disqus.com
.. _django-disqus: http://django-disqus.readthedocs.org/en/latest/
.. _Backlinks: http://www.backlinks.com
.. _`Text Link Ads`: http://www.matomyseo.com/
.. _MatomySEO: http://www.matomyseo.com/
