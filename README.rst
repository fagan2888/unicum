
Python library *unicum*
-----------------------

.. image:: https://img.shields.io/codeship/dcea6660-ba19-0137-ce69-728d1edfce58/master.svg
   :target: https://codeship.com//projects/364766
   :alt: Codeship

.. image:: https://travis-ci.org/sonntagsgesicht/unicum.svg?branch=master
   :target: https://travis-ci.org/sonntagsgesicht/unicum
   :alt: Travis ci

.. image:: https://readthedocs.org/projects/unicum/badge
   :target: http://unicum.readthedocs.io
   :alt: Read the Docs

.. image:: https://img.shields.io/codefactor/grade/github/sonntagsgesicht/unicum/master
   :target: https://www.codefactor.io/repository/github/sonntagsgesicht/unicum
   :alt: CodeFactor Grade

.. image:: https://img.shields.io/codeclimate/maintainability/sonntagsgesicht/unicum
   :target: https://codeclimate.com/github/sonntagsgesicht/unicum/maintainability
   :alt: Code Climate maintainability

.. image:: https://img.shields.io/codeclimate/coverage/sonntagsgesicht/unicum
   :target: https://codeclimate.com/github/sonntagsgesicht/unicum/test_coverage
   :alt: Code Climate Coverage

.. image:: https://img.shields.io/lgtm/grade/python/g/sonntagsgesicht/unicum.svg
   :target: https://lgtm.com/projects/g/sonntagsgesicht/unicum/context:python/
   :alt: lgtm grade

.. image:: https://img.shields.io/lgtm/alerts/g/sonntagsgesicht/unicum.svg
   :target: https://lgtm.com/projects/g/sonntagsgesicht/unicum/alerts/
   :alt: total lgtm alerts

.. image:: https://img.shields.io/github/license/sonntagsgesicht/unicum
   :target: https://github.com/sonntagsgesicht/unicum/raw/master/LICENSE
   :alt: GitHub

.. image:: https://img.shields.io/github/release/sonntagsgesicht/unicum?label=github
   :target: https://github.com/sonntagsgesicht/unicum/releases
   :alt: GitHub release

.. image:: https://img.shields.io/pypi/v/unicum
   :target: https://pypi.org/project/unicum/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/unicum
   :target: https://pypi.org/project/unicum/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/dm/unicum
   :target: https://pypi.org/project/unicum/
   :alt: PyPI Downloads


`unicum` consists of multiple object implementations that implement various factory pattern.
All types merge into on type `VisibleObject` and each type contributes bits and piece.

The visible obj focus on robust and simple construction from a dictionary via `PersistentObject`
having values only simple types or containers containers of simple types.

These values are translated via `FatoryObject` into more complex structures which are take from a factory.

Or, alternatively, using `DataRange` into something similar to a `data_frame` type in `R`,
a table with column and row names as well as common types for each column values.

Inheriting from `LinkedObject` provides functionality to swap or update attributes at runtime


Example Usage
-------------

Using `FactoryObject`:

.. code-block:: python

    >>> from unicum import FactoryObject

    >>> class Currency(FactoryObject): __factory = dict()
    >>> class EUR(Currency): pass
    >>> class USD(Currency): pass

    >>> EUR().register()  # registers USD() instance with class name 'EUR'
    >>> eur = Currency('EUR')  # picks instance with key 'EUR' from currency cache
    >>> eur == EUR()  # picks instance with key given by class name 'EUR' from currency cache, too.

    True

    >>> eur2 = eur.__class__('EUR')  # picks instance with key 'EUR' from currency cache
    >>> eur == eur2

    True

    >>> usd = USD().register()  # registers USD() instance with class name 'USD'
    >>> usd.register('usd')  # registers usd with name 'usd'
    >>> usd == USD()

    True

    >>> eur == eur.__class__('USD')

    False

    >>> usd == eur.__class__('USD')

    True

    >>> usd == Currency('usd')

    True


Using `LinkedObject`:

.. code-block:: python

    >>> from unicum import LinkedObject


Development Version
-------------------

The latest development version can be installed directly from GitHub:

.. code-block:: bash

    $ pip install --upgrade git+https://github.com/sonntagsgesicht/unicum.git


Contributions
-------------

.. _issues: https://github.com/sonntagsgesicht/unicum/issues
.. __: https://github.com/sonntagsgesicht/unicum/pulls

Issues_ and `Pull Requests`__ are always welcome.


License
-------

.. __: https://github.com/sonntagsgesicht/unicum/raw/master/LICENSE

Code and documentation are available according to the Apache Software License (see LICENSE__).


