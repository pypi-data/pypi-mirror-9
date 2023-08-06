.. _misc:

Miscellaneous
=============

Constructing API URLs
---------------------

See the `ChemSpider API documentation`_ for more details.

    >>> cs.construct_api_url('MassSpec', 'GetExtendedCompoundInfo', csid='2157')
    u'http://www.chemspider.com/MassSpec.asmx/GetExtendedCompoundInfo?csid=2157'

Data sources
------------

Get a list of data sources in ChemSpider::

    >>> cs.get_databases()
    ['Abacipharm', 'Abblis Chemicals', 'Abcam', 'ABI Chemicals', 'Abmole Bioscience', 'ACB Blocks', 'Accela ChemBio', ... ]



.. _`ChemSpider API documentation`: http://www.chemspider.com/AboutServices.aspx
