.. _overview:

########
Overview
########

What django-rblog is
*********************

As name says, `django-rblog` is yet another blog application for Django_. It
started being a pet project to play with Django_. Then the author decided to
create a pip_ installable application because there will be more than one
site running this software and then the features started to improve.

So, `django-rblog` is an application ready to have a blog with tags, images, feeds,
django administration and so much fun.


Features
********

The main feature is that it's easy to use, feel free to test it and, if you see
any missing feature please let us know or simply get involved into the project.
New members, ideas and feateures are welcomed.

Basic features
^^^^^^^^^^^^^^

* Easy to use
* Fully integrated with Django_ administration.
* Posts can be tagged.
* Scheduling posts.
* Images attached to a post (django-rgallery).
* Videos attached to a post (django-rgallery).
* Disqus comments easily integrated.
* You can configure the language of every post (just in case you post in more
  than one language).
* Syndicate everywhere, last posts, tags...

Technical features
^^^^^^^^^^^^^^^^^^

As ``setup.py`` says, `django-rblog` uses other 3rd party software to complete
the features. The main ones are the following:

* Django-rblog is a Django_ app.
* Using South_ for migrations.
* PIL_ and sorl-thumbnail_ for the image processor.
* Admin rich textareas with django-tinymce_.
* Tags on posts with django-tagging_.
* Minify and compressed javascript and css files with django-compressor_
* Comments powered by Disqus_ with django-disqus_.

Easy integration
^^^^^^^^^^^^^^^^

* Easy to integrate in yout Django_ project.
* Just install, configure the app and start to write your posts.
* Templates included. Basic templates are included, but you can overwrite
  with yours to fit your needs.

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