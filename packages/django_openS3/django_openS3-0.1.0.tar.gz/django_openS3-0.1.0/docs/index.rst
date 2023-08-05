.. django_openS3 documentation master file, created by
   sphinx-quickstart on Fri Feb  6 00:48:38 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst


Contributions
=============

Thanks for wanting to contribute! To contribute with development time,
fork the repo `logston/django_openS3`_ on GitHub and issue a pull request.

.. _logston/django_openS3: https://github.com/logston/django_openS3

NB. To build the docs, you will need to set the following environment variables.

::

    DJANGO_SETTINGS_MODULE
    AWS_S3_BUCKET
    AWS_S3_ACCESS_KEY
    AWS_S3_SECRET_KEY

**Set these environment variables to dummy values** when building the docs just in
case they some how sneak into the docs.

Contents:

.. toctree::
   :maxdepth: 2

   storage
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

