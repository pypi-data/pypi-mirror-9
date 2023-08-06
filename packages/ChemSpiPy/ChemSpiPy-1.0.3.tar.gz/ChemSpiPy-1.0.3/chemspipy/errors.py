# -*- coding: utf-8 -*-
"""
chemspipy.errors
~~~~~~~~~~~~~~~~

Exceptions raised by ChemSpiPy.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


class ChemSpiPyError(Exception):
    """Root ChemSpiPy Exception."""
    pass


class ChemSpiPyParseError(ChemSpiPyError):
    """Raised when ChemSpiPy fails to parse a response from the ChemSpider servers."""
    pass


class ChemSpiPyAuthError(ChemSpiPyError):
    """Raised when the security token doesn't have access to an endpoint."""
    pass


class ChemSpiPyNotFoundError(ChemSpiPyError):
    """Raised when no record is present for the requested CSID."""
    pass


class ChemSpiPyTimeoutError(ChemSpiPyError):
    """Raised when an asynchronous request times out."""
    pass


class ChemSpiPyServerError(ChemSpiPyError):
    """Raised when ChemSpider returns a 500 status code with an error message."""
    pass
