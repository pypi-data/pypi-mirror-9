======================================
attrs: Attributes without boilerplate.
======================================

.. image:: https://pypip.in/version/attrs/badge.svg
   :target: https://pypi.python.org/pypi/attrs/
   :alt: Latest Version

.. image:: https://travis-ci.org/hynek/attrs.svg
   :target: https://travis-ci.org/hynek/attrs
   :alt: CI status

.. image:: https://coveralls.io/repos/hynek/attrs/badge.png?branch=master
   :target: https://coveralls.io/r/hynek/attrs?branch=master
   :alt: Current coverage

.. teaser-begin

``attrs`` is an `MIT <http://choosealicense.com/licenses/mit/>`_-licensed Python package with class decorators that ease the chores of implementing the most common attribute-related object protocols:

.. code-block:: pycon

   >>> import attr
   >>> @attr.s
   ... class C(object):
   ...     x = attr.ib(default=42)
   ...     y = attr.ib(default=attr.Factory(list))
   >>> i = C(x=1, y=2)
   >>> i
   C(x=1, y=2)
   >>> i == C(1, 2)
   True
   >>> i != C(2, 1)
   True
   >>> attr.asdict(i)
   {'y': 2, 'x': 1}
   >>> C()
   C(x=42, y=[])
   >>> C2 = attr.make_class("C2", ["a", "b"])
   >>> C2("foo", "bar")
   C2(a='foo', b='bar')

(If you don’t like the playful ``attr.s`` and ``attr.ib``, you can also use their no-nonsense aliases ``attr.attributes`` and ``attr.attr``).

You just specify the attributes to work with and ``attrs`` gives you:

- a nice human-readable ``__repr__``,
- a complete set of comparison methods,
- an initializer,
- and much more

*without* writing dull boilerplate code again and again.

This gives you the power to use actual classes with actual types in your code instead of confusing ``tuple``\ s or confusingly behaving ``namedtuple``\ s.

So put down that type-less data structures and welcome some class into your life!

.. note::
   I wrote an `explanation <https://attrs.readthedocs.org/en/latest/why.html#characteristic>`_ on why I forked my own ``characteristic``.
   It's not dead but ``attrs`` will have more new features.

``attrs``\ ’s documentation lives at `Read the Docs <https://attrs.readthedocs.org/>`_, the code on `GitHub <https://github.com/hynek/attrs>`_.
It’s rigorously tested on Python 2.6, 2.7, 3.3+, and PyPy.


Authors
-------

``attrs`` is written and maintained by `Hynek Schlawack <https://hynek.me/>`_.

The development is kindly supported by `Variomedia AG <https://www.variomedia.de/>`_.

It’s the spiritual successor of `characteristic <https://characteristic.readthedocs.org/>`_ and aspires to fix some of it clunkiness and unfortunate decisions.  Both were inspired by Twisted’s `FancyEqMixin <https://twistedmatrix.com/documents/current/api/twisted.python.util.FancyEqMixin.html>`_ but both are implemented using class decorators because `sub-classing is bad for you <https://www.youtube.com/watch?v=3MNVP9-hglc>`_, m’kay?


The following folks helped forming ``attrs`` into what it is now:

- `Glyph <https://github.com/glyph/>`_
- `HawkOwl <https://github.com/hawkowl>`_
- `Lynn Root <https://github.com/econchick>`_
- `Wouter Bolsterlee <https://github.com/wbolster/>`_

Of course ``characteristic``\ ’s `hall of fame <https://characteristic.readthedocs.org/en/stable/license.html>`_ applies as well since they share a lot of code.


