django_openS3
=============

|docs| |tests|

An openS3 wrapper for use with Django.


Installation
============

::

   $ pip install django_openS3

To install the latest development version::

    $ git clone git@github.com:logston/django_openS3.git
    $ cd django_openS3
    $ python setup.py install


Usage
=====

::

    # Add django_openS3 to your project's list of installed apps.
    INSTALLED_APPS = [
        ...
        'django_openS3',
        ...
    ]

    # Set your desired bucket and authentication/authorization info.
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_S3_BUCKET']
    AWS_ACCESS_KEY_ID = os.environ['AWS_S3_ACCESS_KEY']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_S3_SECRET_KEY']

    # Tell django to use django_openS3 for storing static files and media.
    DEFAULT_FILE_STORAGE = 'django_openS3.storage.S3MediaStorage'
    STATICFILES_STORAGE = 'django_openS3.storage.S3StaticStorage'

    # Optionally set the directories in which static and media
    # files will be saved to. Defaults are listed below.
    S3_STATIC_DIR = '/static/'
    S3_MEDIA_DIR = '/media/'

Bug Tracker
===========

Please report bugs!!
`Report bugs at django_openS3's GitHub repo <https://github.com/logston/django_openS3/issues>`_.

Further Documentation
=====================

Further documentation can be found on `Read the Docs`_.

.. _Read the Docs: http://django_opens3.readthedocs.org/en/latest/

.. |docs| image:: https://readthedocs.org/projects/django_opens3/badge/
    :alt: Documentation Status
    :scale: 100%
    :target: http://django_opens3.readthedocs.org/en/latest/

.. |tests| image:: https://travis-ci.org/logston/django_openS3.svg
    :target: https://travis-ci.org/logston/django_openS3