gurobimh: Unofficial Alternative Gurobi/Python Interface
========================================================

Overview
--------
`gurobimh` is a drop-in replacement for the `gurobipy` API bindings shipped with
[Gurobi](www.gurobi.com). It offers several advantages:

* `gurobimh` can be compiled for all current versions of Python; you do not need
  to rely on Gurobi officially supporting your desired Python version.
* `gurobimh`'s performance is much better, especially when modifying models a lot (like in a hand-written
  branch and bound solver).
* `gurobimh` is free software an can be easily extended.
* `gurobimh` ships a Cython `pxd` files, and the `Model` class has some fast-access `cdef` member
  methods for model modifications or queries than circumvent some of the slower API parts. This
  means that, if you are writing your algorithms in Cython, you can almost achieve the performance
  of the C interface, but using a much cleaner API.
  
Of course, there are also disatvantages:
* Up to now, `gurobimh` supports only a subset of the official `gurobipy` API, in particular
  quadratic programming is not yet supported, and lots of parameters are missing. However these
  features are easy to implement once you look at how the others are, so you are welcome to
  contribute. Simply put, I have only implemented the features I am using myself.
* Though I have successfully verified that `gurobimh` behaves like `gurobipy` for my programs,
  there are probably lots of bugs, and of course there's no commercial support. Don't use in
  productive environments!

Requirements
------------
The API is written in [Python](www.python.org). To compile it, you need [Cython](www.cython.org). Of
course, you need to have Gurobi installed, and the `GUROBI_HOME` environment variable needs to be
set correctly.

Installation
------------
Install directly from the [Python Package Index](www.pypi.org) with

    pip install gurobimh
    
Alternatively, download the package and type:

    python setup.py install


Both commands can be appended by the `--user` option which locally installs `gurobimh` for the
current user without needing root privileges.


Usage
-----
Simply replace any `gurobipy` import statements with `gurobimh`. If anything goes wrong, file a bug!

Contact
-------
Please contact [me](helmling@uni-koblenz.de) or use the GitHub features for comments, bugs etc.