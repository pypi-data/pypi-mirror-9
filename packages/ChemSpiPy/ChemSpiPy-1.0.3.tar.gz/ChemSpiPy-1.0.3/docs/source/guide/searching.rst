.. _searching:

Searching
=========

ChemSpiPy provides a number of different ways to search ChemSpider.

Compound search
---------------

The main ChemSpiPy search method functions in a similar way to the main search box on the ChemSpider website. Just
provide any type of query, and ChemSpider will interpret it and provide the most relevant results::

    >>> cs.search('O=C(OCC)C')
    Results([Compound(8525)])
    >>> cs.search('glucose')
    Results([Compound(5589), Compound(58238), Compound(71358), Compound(96749), Compound(9312824), Compound(9484839)])
    >>> cs.search('2157')
    Results([Compound(2157)])

The supported query types include systematic names, synonyms, trade names, registry numbers, molecular formula, SMILES,
InChI and InChIKey.

The :class:`~chemspipy.Results` object that is returned can be treated just like any regular python list. For example,
you can iterate over the results::

    >>> for result in cs.search('Glucose'):
    ...    print(result.csid)
    5589
    58238
    71358
    96749
    9312824
    9484839

The :class:`~chemspipy.Results` object also provides the time take to perform the search, and a message that explains
how the query type was resolved::

    >>> r = cs.search('Glucose')
    >>> print(r.duration)
    u'0:00:00.017'
    >>> print(r.message)
    u'Found by approved synonym'

Asynchronous searching
----------------------

Certain types of search can sometimes take slightly longer, which can be inconvenient if the search method blocks the
Python interpreter until the search results are returned. Fortunately, the ChemSpiPy search method works asynchronously.

Once a search is executed, ChemSpiPy immediately returns the :class:`~chemspipy.Results` object, which is actually
empty at first::

    >>> results = cs.search('O=C(OCC)C')
    >>> print(results.ready())
    False

In a background thread, ChemSpiPy is making the search request and waiting for the response. But in the meantime, it is
possible to continue performing other tasks in the main Python interpreter process. Call ``ready()`` at any
point to check if the results have been returned and are available.

Any attempt to access the results will just block until the results are ready, like a simple synchronous search. To
manually block the main thread until the results are ready, use the ``wait()`` method::

    >>> results.wait()
    >>> results.ready()
    True

For more detailed information about the status of a search, use the ``status`` property::

    >>> results.status
    u'Created'
    >>> results.wait()
    >>> results.status
    u'ResultReady'

The possible statuses are ``Unknown``, ``Created``, ``Scheduled``, ``Processing``, ``Suspended``,
``PartialResultReady``, ``ResultReady``.

Simple search
-------------

The asynchronous search is designed to be simple as possible, but it's possible that the additional overhead might be
overkill in some cases. The ``simple_search`` method provides a simpler synchronous alternative. Use it in the same way::

    >>> cs.simple_search('Glucose')
    [Compound(5589), Compound(58238), Compound(71358), Compound(96749), Compound(9312824), Compound(9484839)]

In this case, the main Python thread will be blocked until the search results are returned, and the results actually are
just in a regular Python list. A maximum of 100 results are returned.

Search by formula
-----------------

Searching by molecular formula is supported by the main ``search`` method, but there is the possibility that a formula
could be interpreted as a name or SMILES or another query type. To specifically search by formula, use::

    >>> cs.search_by_formula('C44H30N4Zn')
    [Compound(436642), Compound(3232330), Compound(24746832), Compound(26995124)]

Search by mass
--------------

It is also possible to search ChemSpider by mass by specifying a certain range::

    >>> cs.search_by_mass(680, 0.001)
    [Compound(8298180), Compound(12931939), Compound(12931969), Compound(21182158)]

The first parameter specifies the desired molecular mass, while the second parameter specifies the allowed ± range of
values.
