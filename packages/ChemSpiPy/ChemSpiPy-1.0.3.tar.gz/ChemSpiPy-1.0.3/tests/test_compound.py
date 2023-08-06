# -*- coding: utf-8 -*-
"""
test_compound
~~~~~~~~~~~~~

Test the Compound object.

:copyright: Copyright 2014 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import logging
import os

import nose
from nose.tools import eq_, ok_, assert_not_equal
import requests

from chemspipy import ChemSpider, Compound, Spectrum


logging.basicConfig(level=logging.WARN, format='%(levelname)s:%(name)s:(%(threadName)-10s):%(message)s')
logging.getLogger('chemspipy').setLevel(logging.DEBUG)

# Security token is retrieved from environment variables
CHEMSPIDER_SECURITY_TOKEN = os.environ['CHEMSPIDER_SECURITY_TOKEN']
cs = ChemSpider(security_token=CHEMSPIDER_SECURITY_TOKEN)


def test_get_compound():
    """Test getting a compound by ChemSpider ID."""
    compound = cs.get_compound(2157)
    ok_(isinstance(compound, Compound))
    eq_(compound.csid, 2157)
    compound = cs.get_compound('2157')
    ok_(isinstance(compound, Compound))
    eq_(compound.csid, 2157)


def test_get_compounds():
    """Test getting multiple compounds by ChemSpider ID."""
    compounds = cs.get_compounds([2157, 13837760])
    eq_([c.csid for c in compounds], [2157, 13837760])
    for c in compounds:
        ok_('http://' in c.image_url)
        ok_(c.average_mass > 0)


def test_compound_init():
    """Test instantiating a Compound directly."""
    compound = Compound(cs, 2157)
    eq_(compound.csid, 2157)


def test_compound_equality():
    """Test equality test by ChemSpider ID."""
    c1 = cs.get_compound(13837760)
    c2 = cs.get_compound(2157)
    c3 = cs.get_compound(2157)
    assert_not_equal(c1, c2)
    eq_(c2, c3)


def test_compound_repr():
    """Test Compound object repr."""
    eq_(repr(cs.get_compound(1234)), 'Compound(1234)')


def test_image_url():
    """Test image_url returns a valid URL."""
    url = cs.get_compound(2157).image_url
    response = requests.get(url)
    ok_('http://www.chemspider.com/ImagesHandler.ashx?id=' in url)
    eq_(response.status_code, 200)


def test_molecular_formula():
    """Test Compound property molecular_formula."""
    compound = cs.get_compound(2157)
    eq_(compound.molecular_formula, 'C_{9}H_{8}O_{4}')
    # Ensure value is the same on subsequent access from cache
    eq_(compound.molecular_formula, 'C_{9}H_{8}O_{4}')


def test_smiles():
    """Test Compound property smiles."""
    compound = cs.get_compound(2157)
    eq_(compound.smiles, 'CC(=O)Oc1ccccc1C(=O)O')
    # Ensure value is the same on subsequent access from cache
    eq_(compound.smiles, 'CC(=O)Oc1ccccc1C(=O)O')


def test_inchi():
    """Test Compound property inchi."""
    compound = cs.get_compound(2157)
    eq_(compound.inchi, 'InChI=1/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)')
    # Ensure value is the same on subsequent access from cache
    eq_(compound.inchi, 'InChI=1/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)')


def test_inchikey():
    """Test Compound property inchikey."""
    compound = cs.get_compound(2157)
    eq_(compound.inchikey, 'BSYNRYMUTXBXSQ-UHFFFAOYAW')
    # Ensure value is the same on subsequent access from cache
    eq_(compound.inchikey, 'BSYNRYMUTXBXSQ-UHFFFAOYAW')


def test_masses():
    """Test Compound property average_mass, molecular_weight, monoisotopic_mass, nominal_mass."""
    compound = cs.get_compound(2157)
    ok_(180 < compound.average_mass < 180.2)
    ok_(180 < compound.molecular_weight < 180.2)
    ok_(180 < compound.monoisotopic_mass < 180.2)
    eq_(compound.nominal_mass, 180)


def test_descriptors():
    """Test Compound property alogp, xlogp."""
    compound = cs.get_compound(348191)
    eq_(compound.alogp, 0.0)
    eq_(compound.xlogp, 1.2)


def test_name():
    """Test Compound property common_name."""
    compound = cs.get_compound(2157)
    eq_(compound.common_name, 'Aspirin')


def test_molfiles():
    """Test Compound property mol2d, mol3d, mol_raw."""
    compound = cs.get_compound(2157)
    ok_('V2000' in compound.mol_2d)
    ok_('V2000' in compound.mol_3d)
    ok_('V2000' in compound.mol_raw)


def test_image():
    """Test Compound property image."""
    compound = cs.get_compound(2157)
    eq_(compound.image[:8], b'\x89PNG\x0d\x0a\x1a\x0a')  # PNG magic number


def test_spectra():
    """Test Compound property spectra."""
    compound = cs.get_compound(2157)
    for s in compound.spectra:
        ok_(isinstance(s, Spectrum))
        eq_(s.csid, 2157)
        ok_(isinstance(s.spectrum_id, int))
    compound = cs.get_compound(263)
    eq_(compound.spectra, [])


if __name__ == '__main__':
    nose.main()
