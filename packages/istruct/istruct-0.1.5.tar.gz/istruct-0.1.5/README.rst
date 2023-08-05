istruct
=======
Immutable struct built on top of ``collections.namedtuple`` with sane defaults

Goals
-----
- Immutable, dictionary-like data structure (Note: ``istruct`` is *not* an immutable version of the existing ``struct`` in Python)
- Minimal
- Support required *and* optional fields (with default values)
- Strictly disallow positional arguments

Installation
------------

``pip install istruct``

Quick Start
-----------
First, create an ``istruct`` object called ``person`` where ``first_name`` and ``last_name`` are *required* whereas ``middle_name``, ``dob`` and ``email`` are *optional* (with default values specified).

.. code-block:: python

    In [1]: from istruct import istruct

    In [2]: person = istruct("first_name", "last_name", middle_name="", dob="2000-01-01", email=None)

Then, create an instance of ``person`` with ``first_name``, ``last_name`` and ``middle_name``.

.. code-block:: python

    In [3]: p = person(first_name="Jim", last_name="Raynor", middle_name="Eugene")

    In [4]: p
    Out[4]: istruct(first_name='Jim', last_name='Raynor', email=None, dob='2000-01-01', middle_name='Eugene')

You can retrieve field values like you would normally do.

.. code-block:: python

    In [5]: p.first_name
    Out[5]: 'Jim'

    In [6]: p.dob
    Out[6]: '2000-01-01'

``p`` is immutable, meaning that it cannot be modified after created. Thus, set/delete operations like below would fail, raising an ``AttributeError``.

.. code-block:: python

    In [7]: p.first_name = "James"
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    <ipython-input-13-681faedb279a> in <module>()
    ----> 1 p.first_name = "James"

    AttributeError: can't set attribute

    In [8]: del p.email
    ---------------------------------------------------------------------------
    AttributeError                            Traceback (most recent call last)
    <ipython-input-12-d5c698764d13> in <module>()
    ----> 1 del p.email

    AttributeError: can't delete attribute

``istruct`` only accepts named/keyword arguments. It strictly disallows positional arguments by design.

.. code-block:: python

    In [9]: p = person("Jim", "Raynor")
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    <ipython-input-6-c0bdbd269e9f> in <module>()
    ----> 1 p = person("Jim", "Raynor")

    /home/microamp/devel/projs/istruct/istruct/__init__.py in _istruct(*positional, **attrs)
         49         if positional:
         50             raise TypeError("No positional arguments are allowed in istruct "
    ---> 51                             "(%d found)" % (len(positional),))
         52
         53         nt = namedtuple(__name__,

    TypeError: No positional arguments are allowed in istruct (2 found)

``istruct`` would raise a ``TypeError`` when one or more *required* fields are omitted.

.. code-block:: python

    In [10]: p = person(last_name="Raynor")
    ---------------------------------------------------------------------------
    TypeError                                 Traceback (most recent call last)
    <ipython-input-15-451d2add9ee8> in <module>()
    ----> 1 p = person(last_name="Raynor")

    /home/microamp/devel/projs/istruct/istruct.py in _istruct(**attrs)
         25     def _istruct(**attrs):
         26         nt = namedtuple(name(), merge_tuples(args, tuple(kwargs.keys())))
    ---> 27         return nt(**merge_dicts(kwargs, attrs))
         28
         29     return _istruct

    TypeError: __new__() missing 1 required positional argument: 'first_name'

Versions Tested
---------------
- Python 2.7
- Python 3.2
- Python 3.3
- Python 3.4
- PyPy
- PyPy3

TODO
----
- Find ways to annotate types

License
-------
MIT
