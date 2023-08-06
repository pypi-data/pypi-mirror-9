#########
staticargs
#########
**A clean way to work around mutable default arguments in python functions**

Get staticargs
=============

staticargs supports Python 2 and 3.  Tests are run for 2.7 and 3.4

.. code-block:: shell

    pip install staticargs

Run the tests
=============
You must install tox, then run:

.. code-block:: shell

    git clone https://github.com/HurricaneLabs/staticargs.git
    cd staticargs
    tox

Example
--------

First view the problem we are going to solve:

.. code-block:: python

    >>> def append_cat(cats=[]):
    ...     cats.append("cat")
    ...     return cats
    ...
    >>> print(append_cat())
    ['cat']
    >>> print(append_cat())
    ['cat', 'cat']
    >>> print(append_cat())
    ['cat', 'cat', 'cat']
    >>>

Well that's not good!  Notice how even though we are appending "cat" only once, the number of items in the list returned gets bigger each time.  Learn more about this problem and some other Python gotchas by watching this amazing presentation from PyCon 2015 (this specific problem is discussed at 8:04):  https://youtu.be/sH4XF6pKKmk

staticargs solves this problem for you:

.. code-block:: python

    >>> from staticargs import staticargs
    >>> import random
    >>>
    >>> @staticargs
    ... def append_cat(cats=[]):
    ...     #I love cats
    ...     cats.append("cat")
    ...     return cats
    ...
    >>> print(append_cat())
    ['cat']
    >>> print(append_cat())
    ['cat']
    >>> print(append_cat())
    ['cat']
    >>>
    >>> @staticargs
    ... def store_dog(dogs={}):
    ...     #Dogs are OK I guess
    ...     dog_name = random.choice(["rufus", "muffins", "scooby"])
    ...     dogs[dog_name] = "good boy"
    ...     return dogs
    ...
    >>> print(store_dog())
    {'muffins': 'good boy'}
    >>> print(store_dog())
    {'scooby': 'good boy'}
    >>> print(store_dog())
    {'rufus': 'good boy'}
    >>>
