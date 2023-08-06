.. _intro:

Introduction
============

ChemSpiPy is a Python wrapper that allows simple access to the web APIs offered by ChemSpider. The aim is to provide an
interface for users to access and query the ChemSpider database using Python, facilitating programs that can
automatically carry out the tasks that you might otherwise perform manually via the `ChemSpider website`_.

The ChemSpider website has `full documentation for the ChemSpider APIs`_. It can be useful to browse through this
documentation before getting started with ChemSpiPy to get an idea of what sort of features are available.

.. _securitytoken:

Obtaining a security token
--------------------------

Access to the ChemSpider API is free to academic users. Commercial users should contact the ChemSpider team to obtain
access.

Most operations require a "security token" that is issued to you automatically when you `register for a RSC ID`_ and
then sign in to ChemSpider. Once you have done this, you can find your security token on your
`ChemSpider User Profile`_.

Some operations require a further "Service Subscriber" role. Contact the ChemSpider team to discuss upgrading your user
account for access to these features.

ChemSpiPy license
-----------------

.. include:: ../../../LICENSE

.. _`ChemSpider website`: http://www.chemspider.com
.. _`full documentation for the ChemSpider APIs`: http://www.chemspider.com/AboutServices.aspx
.. _`register for a RSC ID`: https://www.rsc.org/rsc-id/sign-in
.. _`ChemSpider User Profile`: http://www.chemspider.com/UserProfile.aspx
