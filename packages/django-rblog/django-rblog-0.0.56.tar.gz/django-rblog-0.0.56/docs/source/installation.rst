.. _installation:

############
Installation
############

If you're used to play with pip_ and virtualenv_ the install process should be
quite easy for you.

***********
Dependencies
***********

This packages deppends on other thirds. You can see the complete list in the
``setup.py`` file. If you're using pip to install this piece of software you
don't have to worry about the dependencies, pip_ does the job.

********************
Installation Methods
********************

You can install `django-rblog` in two different ways, with pip_ or cloning the
oficial repository and hook it to your project with ``python develop`` option.
Pip option is better if you want to install a stable version::

    $ pip install django-rblog

If you want to install the last develop version you can clone the repository
and pull changes as many times as you want::

    $ hg clone https://bitbucket.org/r0sk/django-rblog your/local/path

But the standalone installation has no sense at all. You must install
`django-rblog` as app in a Django_ project.

********************
Project from scratch
********************

Well, it's not so much util to know how to install `django-rblog` if you
don't know how to integrate it in a project. So let me explain how to install
this software in a projec, from scratch.

First of all you need to create a virtualenv_ and install Django_::

    $ mkdir myblog
    $ cd myblog
    $ virtualenv env
      New python executable in env/bin/python
      Installing setuptools............done.
      Installing pip...............done.
    $ . env/bin/activate
    (env)$ pip install "Django<1.5"

Once we have Django_ installed we have to install `django-rblog` in the
enviroment, we can do it following one of the methods we describe above:

Pip method
==========
::

    $ . env/bin/activate
    (env)$ pip install django-rblog
           Downloading/unpacking django-rblog
           [it will resolve the dependencies...]

Cloning develop repo
====================
::

    $ . env/bin/activate
    (env)$ hg clone https://bitbucket.org/r0sk/django-rblog django-rblog
    (env)$ cd django-rblog
    (env)$ python setup.py develop

At this time we have our `myblog` project ready to run the `django-rblog` app,
next step is to start the project and tune the settings.

Starting the project
====================

Once you have installed Django_ and `django-rblog`, you have to start a new
Django project::

    (env)$ django-admin.py startproject project

Now you have to configure the database backend and the other general values you
are used to configure in Django. Next step is to add the ``rblog`` and all the
required apps to ``settings.INSTALLED_APPS`` config directive::

    INSTALLED_APPS += ('south',
                       'tinymce',
                       'filebrowser',
                       'tagging',
                       'sorl.thumbnail',
                       'disqus',
                       'compressor',
                       'rblog', )

Lastly we have to create the project database and migrate it to last
`django-rblog` version::

    (env)$ ./manage.py syncdb
           [Create a Django superuser]

::

    (env)$ ./manage.py migrate rblog --list
           rblog
             ( ) 0001_initial
             ( ) 0002_auto__del_comments__del_field_post_thread_id
             ( ) 0003_auto__add_comments__add_field_post_thread_id
             ( ) 0004_auto__chg_field_post_creation_date
             ...
    (env)$ ./manage.py migrate rblog

And you are done!. See :doc:`configuration` for the next big step.

.. _pip: http://www.pip-installer.org/en/latest/index.html
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _Django: http://djangoproject.org/
