============================================
Contributing to Kwant and reporting problems
============================================

We see Kwant not just as a package with fixed functionality, but rather as a
framework for implementing different physics-related algorithms using a common
set of concepts and, if possible, a shared interface.  We have designed it
leaving room for growth, and plan to keep extending it.

External contributions to Kwant are highly welcome.  You can help to advance
the project not only by writing code, but also by reporting bugs, and
fixing/improving the documentation.  A `mailing list
<http://kwant-project.org/community.html>`_ is available for discussions.

If you have some code that works well with Kwant, or extends it in some useful
way, please consider sharing it.  Any external contribution will be clearly
marked as such, and relevant papers will be added to the list of
:doc:`suggested acknowledgements <citing>`.  The complete development history
is also made available through a `web interface
<http://git.kwant-project.org/kwant>`_.  If you plan to contribute, it is best
to coordinate with us in advance either through the `mailing list
<http://kwant-project.org/community.html>`__, or directly by `email
<mailto:authors@kwant-project.org>`_ for matters that you prefer to not discuss
publicly.

Reporting bugs
--------------

If you encounter a problem with Kwant, first try to reproduce it with as simple
a system as possible.  Double-check with the documentation that what you
observe is actually a bug in Kwant. If you think it is, please check whether
the problem is already known by searching the `mailing list
<http://kwant-project.org/community.html>`__.

If the problem is not known yet, please email a bug report to the `Kwant mailing
list <http://kwant-project.org/community.html>`__. A report should contain:

* The versions of software you are using (Kwant, Python, operating system, etc.)

* A description of the problem, i.e. what exactly goes wrong.

* Enough information to reproduce the bug, preferably in the form of a simple
  script.

How to contribute
-----------------

We use the version control system `Git <http://git-scm.com/>`_ to coordinate the
development of Kwant.  If you are new to Git, we invite you to learn its basics.
(There's a plethora of information available on the Web.)  Kwant's Git
repository contains not only the source code, but also all of the reference
documentation and the tutorial.

It is best to base your work on the latest version of Kwant::

    git clone http://git.kwant-project.org/kwant

Then you can modify the code, and build Kwant and the documentation as described
in the :doc:`installation instructions <install>`.

Some things to keep in mind:

* Please keep the code consistent by adhering to the prevailing naming and
  formatting conventions.  We generally follow the `"Style Guide for Python
  Code" <http://www.python.org/dev/peps/pep-0008/>`_ For docstrings, we follow
  `NumPy's "Docstring Standard"
  <http://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt>`_ and
  `Python's "Docstring Conventions"
  <http://www.python.org/dev/peps/pep-0257/>`_.

* Write tests for all the important functionality you add.  Be sure not to
  break existing tests.

A useful trick for working on the source code is to build in-place so that there
is no need to re-install after each change.  This can be done with the following
command ::

    python setup.py build_ext -i

The ``kwant`` subdirectory of the source distribution will be thus turned into
a proper Python package that can be imported.  To be able to import Kwant from
within Python, one can either work in the root directory of the distribution
(where the subdirectory ``kwant`` is located), or make a (symbolic) link from
somewhere in the Python search path to the the package subdirectory.
