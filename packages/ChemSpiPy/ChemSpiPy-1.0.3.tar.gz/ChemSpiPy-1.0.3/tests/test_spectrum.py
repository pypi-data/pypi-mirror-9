# -*- coding: utf-8 -*-
"""
test_spectrum
~~~~~~~~~~~~~

Test the Spectrum object.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import datetime
import logging
import os

import nose
from nose.tools import eq_, ok_, assert_not_equal
import six

from chemspipy import ChemSpider, Spectrum


logging.basicConfig(level=logging.WARN, format='%(levelname)s:%(name)s:(%(threadName)-10s):%(message)s')
logging.getLogger('chemspipy').setLevel(logging.DEBUG)

# Security token is retrieved from environment variables
CHEMSPIDER_SECURITY_TOKEN = os.environ['CHEMSPIDER_SECURITY_TOKEN']
cs = ChemSpider(security_token=CHEMSPIDER_SECURITY_TOKEN)


def test_get_all_spectra():
    """Test getting all spectra in ChemSpider."""
    spectra = cs.get_all_spectra()
    for s in spectra:
        ok_(isinstance(s, Spectrum))
        ok_(isinstance(s.spectrum_id, int))


def test_get_spectrum():
    """Test getting a spectrum by spectrum ID."""
    s = cs.get_spectrum(36)
    ok_(isinstance(s, Spectrum))
    eq_(s.spectrum_id, 36)
    eq_(s.csid, 235)
    eq_(s.spectrum_type, 'HNMR')
    eq_(s.file_name, 'BenzaldehydeHNMR.jdx')
    eq_(s.submitted_date, datetime.datetime(2007, 8, 8, 20, 18, 36, 593000))


def test_get_spectra():
    """Test getting multiple spectra by spectrum ID."""
    spectra = cs.get_spectra([36, 65])
    eq_(len(spectra), 2)
    for s in spectra:
        ok_(isinstance(s, Spectrum))
        ok_(s.spectrum_id in [36, 65])
        ok_(s.csid in [235, 172])


def test_get_compound_spectra():
    """Test getting all spectra for a specific ChemSpider ID."""
    spectra = cs.get_compound_spectra(2157)
    ok_(len(spectra) > 0)
    for s in spectra:
        ok_(isinstance(s, Spectrum))
        ok_(isinstance(s.spectrum_id, int))
        eq_(s.csid, 2157)


def test_spectrum_init():
    """Test instantiating a Spectrum directly."""
    s = Spectrum(cs, 36)
    ok_(isinstance(s, Spectrum))
    eq_(s.spectrum_id, 36)
    eq_(s.csid, 235)
    eq_(s.spectrum_type, 'HNMR')
    eq_(s.file_name, 'BenzaldehydeHNMR.jdx')
    eq_(s.submitted_date, datetime.datetime(2007, 8, 8, 20, 18, 36, 593000))


def test_spectrum_equality():
    """Test equality test by spectrum ID."""
    s1 = cs.get_spectrum(65)
    s2 = cs.get_spectrum(87)
    s3 = cs.get_spectrum(87)
    assert_not_equal(s1, s2)
    eq_(s2, s3)


def test_spectrum_repr():
    """Test Spectrum object repr."""
    eq_(repr(cs.get_spectrum(65)), 'Spectrum(65)')


def test_comments():
    """Test retrieving comments about a spectrum."""
    s = cs.get_spectrum(36)
    ok_(isinstance(s.comments, six.text_type))
    ok_('Benzaldehyde' in s.comments)


def test_no_comments():
    """Test spectrum with no comments."""
    s = cs.get_spectrum(87)
    eq_(s.comments, None)


def test_original_url():
    """Test retrieving original_url for spectrum."""
    s = cs.get_spectrum(65)
    ok_(isinstance(s.original_url, six.text_type))
    ok_('http://' in s.original_url)


def test_no_original_url():
    """Test spectrum with no original_url."""
    s = cs.get_spectrum(36)
    eq_(s.original_url, None)


def test_url():
    """Test retrieving spectrum url."""
    s = cs.get_spectrum(3558)
    eq_(s.url, 'http://www.chemspider.com/FilesHandler.ashx?type=blob&disp=1&id=3558')
    for compound in cs.search('Aspirin'):
        for spectrum in compound.spectra:
            ok_(spectrum.url.startswith('http://www.chemspider.com/FilesHandler.ashx?type=blob&disp=1&id='))


def test_data():
    """Test downloading spectrum."""
    s = cs.get_spectrum(3558)
    ok_('JCAMP-DX' in s.data)
    ok_('NMR SPECTRUM' in s.data)
    ok_(len(s.data) > 500)


if __name__ == '__main__':
    nose.main()
