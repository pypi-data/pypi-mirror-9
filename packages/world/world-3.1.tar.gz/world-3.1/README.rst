===================================================================
world -- Print mappings between country names and DNS country codes
===================================================================

This script takes a list of Internet top-level domain names and prints out
where in the world those domains originate from.  For example:

    $ world tz us
    tz originates from TANZANIA, UNITED REPUBLIC OF
    us originates from UNITED STATES

Reverse look ups are also supported.

    $ world -r united
    Matches for "united":
      ae: UNITED ARAB EMIRATES
      gb: UNITED KINGDOM
      tz: TANZANIA, UNITED REPUBLIC OF
      uk: United Kingdom (common practice)
      um: UNITED STATES MINOR OUTLYING ISLANDS
      us: UNITED STATES

Only two-letter country codes are supported, since these are the only ones
that were freely available from the ISO_ 3166_ standard.  However, as of
2015-01-09, even these are no longer freely available in a machine readable
format.

This script also knows about non-geographic, generic, USA-centric, historical,
common usage, and reserved top-level domains.


Author
======

`world` is Copyright (C) 2013-2015 Barry Warsaw <barry@python.org>

Licensed under the terms of the GNU General Public License, version 3 or
later.  See the LICENSE.txt file for details.


Project
=======

Project home: https://launchpad.net/world
Report bugs at: https://bugs.launchpad.net/world
Code hosting: https://gitorious.org/python-world/python-world.git


.. _ISO: http://www.iso.org/iso/home.html
.. _3166: http://www.iso.org/iso/home/standards/country_codes/
