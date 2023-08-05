Pipeline
========

Pipeline is an asset packaging library for Django, providing both CSS and
JavaScript concatenation and compression, built-in JavaScript template support,
and optional data-URI image and font embedding.

Installation
------------

To install it, simply: ::

    pip install django-pipeline


Documentation
-------------

For documentation, usage, and examples, see :
http://django-pipeline.readthedocs.org


.. :changelog:

History
=======

1.4.5
=====

* Add ES6/6to5 compiler.
* Fix URL rewriter quote handling. Thanks to Josh Braegger.
* Improve FyleSystemFinder. Thanks to Jon Dufresne.

1.4.4.1
=======

* Remove ruby sass implementation specifics.
* Remove artefacts in package.

1.4.3
=====

* Remove tempdir storage location. Thanks to Kristian Glass.
* Make the SASS compiler compatible with more non-ruby SASS. Thanks to Corrado Primier.

1.4.2
=====

* Fix finder bug. Thanks to Quentin Pradet, Remi and Sam Kuehn for the report
* Update finders documentation. Thanks to Thomas Schreiber, Grégoire Astruc and Tobias Birmili for the report.

1.4.1
=====

* Fix storage logic. Thanks to Quentin Pradet for the report.

1.4.0
=====

* **BACKWARD INCOMPATIBLE** : Renamed templatetags library from ``compressed`` to ``pipeline``.
* **BACKWARD INCOMPATIBLE** : Renamed templatetag ``compressed_js`` to ``javascript``.
* **BACKWARD INCOMPATIBLE** : Renamed templatetag ``compressed_css`` to ``stylesheet``.


