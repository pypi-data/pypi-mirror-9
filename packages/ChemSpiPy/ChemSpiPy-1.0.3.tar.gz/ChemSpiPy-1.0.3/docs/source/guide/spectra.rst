.. _spectra:

Spectra
=======

Many compound records in ChemSpider have spectra associated with them.

Retrieving spectra
------------------

If there are spectra available for a :class:`~chemspipy.Compound`, you can retrieve them using the ``spectra``
property::

    >>> compound = cs.get_compound(2157)
    >>> print(compound.spectra)
    [Spectrum(2303), Spectrum(2304), Spectrum(3558), Spectrum(6639), Spectrum(6640), Spectrum(6641), Spectrum(6642), Spectrum(6643), Spectrum(6644), Spectrum(6645), Spectrum(8553), Spectrum(8554)]





Alternatively, you can get spectra directly by using either the compound ChemSpider ID or the Spectrum ID::

    >>> cs.get_spectrum(362)
    Spectrum(362)
    >>> cs.get_compound_spectra(71358)
    [Spectrum(360), Spectrum(361), Spectrum(3172)]

Spectrum metadata
-----------------

Each :class:`~chemspipy.Spectrum` object has a number of properties::

    >>> spectrum = cs.get_spectrum(3558)
    >>> print(spectrum.spectrum_id)
    3558
    >>> print(spectrum.csid)
    2157
    >>> print(spectrum.spectrum_type)
    HNMR
    >>> print(spectrum.file_name)
    Spectrum_315.jdx
    >>> print(spectrum.comments)
    collected by David Bulger at Oral Roberts University on a JEOL 300 MHz NMR with methanol as the solvent
    >>> print(spectrum.original_url)
    http://onschallenge.wikispaces.com/Exp072
    >>> print(spectrum.url)
    http://www.chemspider.com/FilesHandler.ashx?type=blob&disp=1&id=3558

Spectrum data
-------------

The data file for each spectrum is also available using the data property::

    >>> spectra = cs.get_compound_spectra(2424)
    >>> caffeine_ir = spectra[8]
    >>> print(caffeine_ir.data)

Typically this is in JCAMP-DX format.
