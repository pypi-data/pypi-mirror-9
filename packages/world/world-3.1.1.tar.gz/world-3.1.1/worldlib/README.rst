===================================================================
world -- Print mappings between country names and DNS country codes
===================================================================

This package provides a mapping between top-level domain names and their two
letter ISO_ 3166_ country codes.  This script also knows about non-geographic,
generic, USA-centric, historical, common usage, and reserved top-level
domains.

Both a command line script called ``world`` and a library called ``worldlib``
are available.  The latter can be imported into your Python code for whatever
application you want.


Requirements
============

The command line script ``world`` requires Python 3, but the ``worldlib``
library is compatible with both Python 2.7 and Python 3.


Documentation
=============

A `simple guide`_ to using the library is available within this package.  The
manual is also available `online`_.  A manpage provides information on how to
use the ``world`` command line script.


Project details
===============

Project home: https://launchpad.net/world
Report bugs at: https://bugs.launchpad.net/world
Code hosting: https://gitorious.org/python-world/python-world.git


Author
======

``world`` and ``worldlib`` is Copyright (C) 2013-2015 Barry Warsaw
<barry@python.org>

Licensed under the terms of the GNU General Public License, version 3 or
later.  See the LICENSE.txt file for details.


Table of Contents
=================

.. toctree::
    :glob:

    docs/manpage
    docs/usage
    docs/NEWS


.. _ISO: http://www.iso.org/iso/home.html
.. _3166: http://www.iso.org/iso/home/standards/country_codes/
.. _`simple guide`: docs/using.html
.. _`online`: http://pythonhosted.org/world
