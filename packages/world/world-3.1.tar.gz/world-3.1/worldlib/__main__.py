# Copyright (C) 2013-2015 Barry A. Warsaw
#
# This file is part of world
#
# world is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, version 3 of the License.
#
# world is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# world.  If not, see <http://www.gnu.org/licenses/>.

"""world script main entry point."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'main',
    ]


import sys
import argparse

from worldlib import __version__
from worldlib.database import Database, gTLDs


# As of 2015-01-08, ISO has pulled this link and none of the country codes are
# available for free online afaict.
XMLFILE = ('http://www.iso.org/iso/home/standards/country_codes/'
           'country_names_and_code_elements_xml.htm')


def main():
    parser = argparse.ArgumentParser(
        prog='world',
        description='Top level domain name mapper.')
    parser.add_argument('--version',
                        action='version',
                        version='world {}'.format(__version__))
    # Deprecated; See LP: #1409043
    group_1 = parser.add_argument_group()
    group_1.add_argument('--refresh', action='store_true',
                         help=argparse.SUPPRESS)
    group_1.add_argument('--source', default=None,
                         help=argparse.SUPPRESS)
    group_1.add_argument('--cache', default=None,
                         help=argparse.SUPPRESS)
    group_2 = parser.add_argument_group('Querying')
    group_2.add_argument('-r', '--reverse', action='store_true',
                         help="""\
Do a reverse lookup.  In this mode, the arguments can be any Python regular
expression; these are matched against all TLD descriptions (e.g. country
names) and a list of matches is printed.
""")
    group_2.add_argument('-a', '--all', action='store_true',
                         help='Print the mapping of all top-level domains.')
    parser.add_argument('domain', nargs='*')
    # Be explicit so that the test suite can mock sys.argv.
    args = parser.parse_args(sys.argv[1:])
    # Get the mappings.
    if args.refresh:
        #refresh(XMLFILE if args.source is None else args.source, args.cache)
        print("""\
As of 2015-01-08, the two letter country code source file is no longer
available freely online.  Complain to ISO via:
http://www.iso.org/iso/country_codes.htm
See also LP: #1409043
""", file=sys.stderr)
        sys.exit(1)
    # Lookup.
    db = Database(args.cache)
    if args.all:
        print('Country code top level domains:')
        for cc in sorted(db.ccTLDs):
            print('    {}: {}'.format(cc, db.ccTLDs[cc]))
        # Print the empty string instead of an empty print call for Python 2
        # compatibility with the test suite.  Otherwise we get a stupid
        # TypeError when io.StringIO gets a (Python 2) str instead of unicode.
        print('')
        print('Additional top level domains:')
        for tld in sorted(gTLDs):
            print('    {:6}: {}'.format(tld, gTLDs[tld]))
        return
    newline = False
    for domain in args.domain:
        if args.reverse:
            if newline:
                # Print the empty string instead of an empty print call for
                # Python 2 compatibility with the test suite.  Otherwise we get
                # a stupid TypeError when io.StringIO gets a (Python 2) str
                # instead of unicode.
                print('')
            matches = db.find_matches(domain)
            if len(matches) > 0:
                print('Matches for "{}":'.format(
                    domain, len(matches)))
                for code, country in matches:
                    print('  {}: {}'.format(code, country))
                newline = True
                continue
        else:
            country = db.lookup_code(domain)
            if country is not None:
                print('{} originates from {}'.format(domain, country))
                continue
        print('Where in the world is {}?'.format(domain))


if __name__ == '__main__':                          # pragma: no cover
    main()
