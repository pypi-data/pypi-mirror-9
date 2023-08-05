=============================================
 worldlib -- library for country code lookup
=============================================

To use the ``worldlib`` library, import the database which reads a canned,
pre-generated set of code mappings::

    >>> from worldlib.database import Database
    >>> db = Database()

You can look up a country code::

    >>> print(db.lookup_code('it'))
    ITALY

Country codes are case-insensitive::

    >>> print(db.lookup_code('It'))
    ITALY

You can find all matches for a particular string, which allows you for example
to implement a reverse look up.   The matches are returned sorted in
alphabetical order.  As with code look ups, the match string is case
insensitive::

    >>> for code, country in db.find_matches('United'):
    ...     print(code, 'is', country)
    ae is UNITED ARAB EMIRATES
    gb is UNITED KINGDOM
    tz is TANZANIA, UNITED REPUBLIC OF
    uk is United Kingdom (common practice)
    um is UNITED STATES MINOR OUTLYING ISLANDS
    us is UNITED STATES

You can iterate through all the codes::

    >>> for code in db:
    ...     print(code)
    ac
    ...
    zw
