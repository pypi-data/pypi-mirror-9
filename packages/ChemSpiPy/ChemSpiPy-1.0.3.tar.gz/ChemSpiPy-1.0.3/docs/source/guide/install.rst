.. _install:

Installation
============

ChemSpiPy supports Python versions 2.7, 3.2, 3.3 and 3.4.

There are two required dependencies: `six`_ and `requests`_.

Option 1: Use pip (recommended)
-------------------------------

The easiest and recommended way to install is using pip::

    pip install chemspipy

This will download the latest version of ChemSpiPy, and place it in your `site-packages` folder so it is automatically
available to all your python scripts. It should also ensure that the dependencies `six`_ and `requests`_ are installed.

If you don't already have pip installed, you can `install it using get-pip.py`_::

       curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
       python get-pip.py

Option 2: Download the latest release
-------------------------------------

Alternatively, `download the latest release`_ manually and install yourself::

    tar -xzvf ChemSpiPy-1.0.3.tar.gz
    cd ChemSpiPy-1.0.3
    python setup.py install

The setup.py command will install ChemSpiPy in your `site-packages` folder so it is automatically available to all your
python scripts.

Option 3: Clone the repository
------------------------------

The latest development version of ChemSpiPy is always `available on GitHub`_. This version is not guaranteed to be
stable, but may include new features that have not yet been released. Simply clone the repository and install as usual::

    git clone https://github.com/mcs07/ChemSpiPy.git
    cd ChemSpiPy
    python setup.py install

.. _`six`: http://pythonhosted.org/six/
.. _`requests`: http://docs.python-requests.org/
.. _`install it using get-pip.py`: http://www.pip-installer.org/en/latest/installing.html
.. _`download the latest release`: https://github.com/mcs07/ChemSpiPy/releases/
.. _`available on GitHub`: https://github.com/mcs07/ChemSpiPy
