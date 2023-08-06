langdetect
==========

Port of [language-detection](https://code.google.com/p/language-detection/) (version from 03/03/2014) library to Python.


Installation
============

    $ pip install langdetect


Supported Python versions 2.6, 2.7, 3.x.


Basic usage
===========

To detect the language of the text:

    >>> from langdetect import detect
    >>> detect("War doesn't show who's right, just who's left.")
    'en'
    >>> detect("Ein, zwei, drei, vier")
    'de'

To find out the probabilities for the top languages:

    >>> from langdetect import detect_langs
    >>> detect_langs("Otec matka syn.")
    [sk:0.572770823327, pl:0.292872522702, cs:0.134356653968]


More information
================

This library is a direct port of [language-detection](https://code.google.com/p/language-detection/) from Java to Python. All the classes and methods (even unittsets) are unchanged, so for more information see the project's website or wiki.
