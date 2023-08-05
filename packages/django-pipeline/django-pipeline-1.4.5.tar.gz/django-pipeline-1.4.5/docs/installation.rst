.. _ref-installation:

============
Installation
============

1. Either check out Pipeline from GitHub_ or to pull a release off PyPI_ ::

       pip install django-pipeline


2. Add 'pipeline' to your ``INSTALLED_APPS`` ::

       INSTALLED_APPS = (
           'pipeline',
       )

3. Use a pipeline storage for ``STATICFILES_STORAGE`` ::

        STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

4. Add the ``PipelineFinder`` to ``STATICFILES_FINDERS`` ::

        STATICFILES_FINDERS = (
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
            'pipeline.finders.PipelineFinder',
        )


.. note::
  You need to use ``Django>=1.6`` to be able to use this version of pipeline.

.. _GitHub: http://github.com/cyberdelia/django-pipeline
.. _PyPI: http://pypi.python.org/pypi/django-pipeline

Upgrading to 1.4
================

To upgrade to pipeline 1.4, you will need to follow theses steps:

1. Rewrite all templates like follow

    .. code-block:: python
    
        {% load compressed %}
        {% compressed_js 'group' %}
        {% compressed_css 'group' %}

    .. code-block:: python

        {% load pipeline %}
        {% javascript 'group' %}
        {% stylesheet 'group' %}

2. Add the ``PipelineFinder`` to ``STATICFILES_FINDERS`` ::

        STATICFILES_FINDERS = (
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
            'pipeline.finders.PipelineFinder',
        )


Recommendations
===============

Pipeline's default CSS and JS compressor is Yuglify.
Yuglify wraps UglifyJS and cssmin, applying the default YUI configurations to them.
It can be downloaded from: https://github.com/yui/yuglify/.

If you do not install yuglify, make sure to disable the compressor in your settings.

