=================================================
Enhanced theme based on py3 documentation's theme
=================================================

.. image:: http://img.shields.io/pypi/v/sphinx_py3doc_enhanced_theme.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/sphinx_py3doc_enhanced_theme

.. image:: http://img.shields.io/pypi/dm/sphinx_py3doc_enhanced_theme.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/sphinx_py3doc_enhanced_theme

A theme based on the theme of https://docs.python.org/3/ with some responsive enhancements.

Installation
============

::

    pip install sphinx_py3doc_enhanced_theme

Add this in your documentation's ``conf.py``::

    import sphinx_py3doc_enhanced_theme
    html_theme = "sphinx_py3doc_enhanced_theme"
    html_theme_path = [sphinx_py3doc_enhanced_theme.get_html_theme_path()]

Examples
========

* http://python-aspectlib.readthedocs.org/en/latest/
* http://python-manhole.readthedocs.org/en/latest/


Changelog
=========

1.0.1 (2015-02-24)
------------------

* Match some markup changes in latest Sphinx.

1.0.0 (2015-02-13)
------------------

* Fix depth argument for toctree (contributed by Georg Brandl).

0.1.0 (2014-05-31)
------------------

* First release on PyPI.


