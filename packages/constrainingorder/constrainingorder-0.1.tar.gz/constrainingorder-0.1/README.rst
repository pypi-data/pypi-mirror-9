Constraining Order
==================

Constraining Order is a pure python library for solving certain classes of
constraint satisfaction problems. In particular it contains an implementation
of IntervalSets to represent fairly general sets of real numbers.

Constraining Order is neither very powerful, nor very performant, and for
serious problems there are more powerful solutions available:

* `gecode <http://www.gecode.org>`_ (which looks amazing and superbly documented)
* `or-tools <https://code.google.com/p/or-tools/>`_
* `choco <http://www.choco-solver.org/>`_

The creation of Constraining Order was sparked by the realisation that several
of my projects require the solution of relatively simple constraint
satisfaction problems, while it was unacceptable to pull in a heavy dependency
for that.

The code is hosted on `GitHub <https://github.com>`_:

https://github.com/jreinhardt/constraining-order

Documentation is hosted on `readthedocs <https://readthedocs.org/>`_:

https://constraining-order.readthedocs.org/en/latest/

The API of Constraining Order is slightly inspired by gecode (as I had looked
at its documentation before writing it) and the nomenclature I use roughly
follows

    Tsang, E. Foundations of Constraint Satisfaction Academic Press, 1996

which I used to read up a bit on the topic.

The name `constraining order` is a pun on restraining order, as it was not yet
taken for a software project and even makes a bit of sense as long as you don't
think about it.


