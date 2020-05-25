README
===============================

Welcome in a minimal environment for a ILP prototyping.


Installation
------------

You need Python 3.7 in order to use the environment. If you are using pip, then
use:

::

    $ pip install -r requirements.txt

In case you prefer conda (>=4.6.0) do

::

    $ conda config --set pip_interop_enabled True
    $ pip install -r requirements.txt
    $ conda update --all


Usage
-----

Let's create a clause and see what is inside. There are two ways of creating a
new clause, either by explicit construction using classes

.. code:: python

    >>> from src.logic import *
    >>> c1 = Clause([Literal(Atom(Predicate("p", 2), [Constant("Adam"), Variable("x")]), positive=False)])


or by parsing a string

.. code:: python

    >>> from src.folParsing import parseClause
    >>> c2 = parseClause("p(Adam, fatherOf(Adam)), !p(x, fatherOf(fatherOf(x)))")

While parsing, remember that comma is a separator and brackets are used for term and literal composition. So, do not use these two in names of predicate symbols, etc.

You may simply iterate over literals of a clause, terms of a literal or a composed term.

.. code:: python

    >>> for literal in c2:
    >>> print("literal\t{}\n\thas predicate\t{}\n\tis positive\t{}\nand arguments...".format(literal, literal.atom.predicate, literal.positive))
    >>> for term in literal:
    >>>     if isinstance(term, CompoundTerm):
    >>>        print("\tcompound term\t{}\n\t\twith function symbol\t{}".format(term, term.functor))
    >>>        for argument in term:
    >>>            print("\t\t{}".format(argument))
    >>>     else:
    >>>        print("\t{}\t{}".format(term.__class__, term))

The easiest way to apply a substitution to a clause is to create a substitution, i.e. a dictionary of terms indexed by variables.

.. code:: python

    >>> c3 = parseClause("siblings(x,y,z,w)")
    >>> x = Variable("x")
    >>> y = Variable("y")
    >>> z = Variable("z")
    >>> issac = Constant("Issac")
    >>> kain = Constant("Kain")
    >>> substitution = {x : issac, y : kain, z : x}
    >>> substitutedClause = c3.substitute(substitution)
    >>> print("original clause\t{}\nsubstituted clause\t{}".format(c3, substitutedClause))


After taking the basics, we can move to more complex methods. Let us start with testing theta-subsumption.

.. code:: python

    >>> from src.engine import *
    >>> c4 = parseClause("p(x,y)")
    >>> c5 = parseClause("p(z,w)")
    >>> c4SubsumesC5 = subsumes(c4, c5)
    >>> print("{}\t{}\t{}".format(c4, "theta-subsumes" if c4SubsumesC5 else "does not theta-subsume", c5))
    >>> c5SubsumesC4 = subsumes(c5, c4)
    >>> print("{}\t{}\t{}".format(c5, "theta-subsumes" if c5SubsumesC4 else "does not theta-subsume", c4))


Another functionality, which you do not have to implement by yourself, is computation of lgg.

.. code:: python

    >>> c6 = parseClause("p(A, x, f(x))")
    >>> c7 = parseClause("p(y, f(B), f(f(B))), p(x,z,u)")
    >>> print("lgg of\n\t{}\n\t{}\n\tis\t{}".format(c6, c7, lgg(c6, c7, reduceResult=True)))
    >>>
    >>> c8 = parseClause("p(A, x, x)")
    >>> c9 = parseClause("p(y, B, A), p(z, x, u)")
    >>> print("lgg of\n\t{}\n\t{}\n\tis\t{}".format(c8, c9, lgg(c8, c9, reduceResult=True)))


The last functionality, which can very beneficial for you, is computation of least Herbrand model, which, informally, computes all
provable facts given a set of ground facts and a set of definite range-restricted rules.

.. code:: python

    >>> rules = [parseClause("!edge(x,y), edge(y,x)")]
    >>> graph = [literal.atom for literal in parseClause("edge(1,2), edge(2,3), edge(4,3)")]
    >>> extendedGraph = leastHerbrandModel(rules,graph)
    >>> print("The least Herbrand model of given rules and data is\t{}".format(", ".join(str(a) for a in extendedGraph)))

