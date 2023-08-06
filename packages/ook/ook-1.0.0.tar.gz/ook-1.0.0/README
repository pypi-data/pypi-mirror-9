
=============================================
ook - Python-version-sensitive monkeypatching
=============================================

:Author: Zero Piraeus
:Contact: z@etiol.net

**ook** is a simple library to assist with monkeypatching Python methods and
functions on a per-Python-version basis. It provides one decorator, ``patch``,
which conditionally patches callables depending on which version of Python is
running.


Example
-------

Adding the ``compress()`` function to Python 2.6's ``itertools`` module::

    import itertools
    from ook import patch

    # http://docs.python.org/2.7/library/itertools.html#itertools.compress

    @patch(itertools, 2.6)
    def compress(data, selectors):
        # compress('ABCDEF', [1,0,1,0,1,1]) --> A C E F
        return (d for d, s in itertools.izip(data, selectors) if s)


Usage
-----

``patch`` accepts an arbitrary number of version arguments, in a variety of
formats::

    @patch(some.module.or.class, 2.7, "2.6.8", (3, 2, 5), 3)
    def method_or_function(signature):
        """Do something."""
        pass

... as well as ``min`` and ``max`` keyword arguments::

    @patch(some.module.or.class, min="2.6.5", max=2.7)
    def method_or_function(signature):
        """Do something."""
        pass

... which can be combined::

    @patch(some.module.or.class, "3.2.5", max=3.2)
    def method_or_function(signature):
        """Do something."""
        pass

**Note**: If you specify both keyword and non-keyword version arguments, the
patch will only take effect if both the explicitly specified versions and the
implied version ranges are satisfied.

With no arguments other than the module or class to be patched, ``patch``
applies the patch regardless of Python version::

    @patch(some.module.or.class)
    def method_or_function(signature):
        """Do something, no matter what."""
        pass


Installation
------------

This should do the trick::

    pip install ook


Credits / Copyright
-------------------

**ook** was (cough) "inspired" by Guido van Rossum's monkeypatch_ recipe.
Thanks, Guido :-)

It's released under the GNU General Public License (version 3 or later), a copy
of which is included with this distribution in the file **COPYING**.


.. _monkeypatch: http://mail.python.org/pipermail/python-dev/2008-January/076194.html

