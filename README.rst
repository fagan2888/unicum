======
unicum
======

.. image:: https://img.shields.io/codeship/433f24a0-9d5e-0134-66ae-4e318545e956/master.svg
    :target: https://codeship.com//projects/188629

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

Using `SingletonObject`:

.. code-block:: python

    >>> from unicum import SingletonObject

    >>> class MySingleton(SingletonObject): pass

    >>> s1 = MySingleton()
    >>> s2 = MySingleton()

    >>> s1 = s2

    True


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

    $ pip install --upgrade git+https://github.com/pbrisk/unicum.git


Contributions
-------------

.. _issues: https://github.com/pbrisk/unicum/issues
.. __: https://github.com/pbrisk/unicum/pulls

Issues_ and `Pull Requests`__ are always welcome.


License
-------

.. __: https://github.com/pbrisk/unicum/raw/master/LICENSE

Code and documentation are available according to the Apache Software License (see LICENSE__).


