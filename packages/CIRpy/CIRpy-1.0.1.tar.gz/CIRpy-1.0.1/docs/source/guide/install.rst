.. _install:

Installation
============

CIRpy supports Python versions 2.7, 3.2, 3.3 and 3.4. There are no required dependencies.

Option 1: Use pip (recommended)
-------------------------------

The easiest and recommended way to install is using pip::

    pip install cirpy

This will download the latest version of CIRpy, and place it in your `site-packages` folder so it is automatically
available to all your python scripts.

If you don't already have pip installed, you can `install it using get-pip.py`_::

       curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
       python get-pip.py

Option 2: Download the latest release
-------------------------------------

Alternatively, `download the latest release`_ manually and install yourself::

    tar -xzvf CIRpy-1.0.1.tar.gz
    cd CIRpy-1.0.1
    python setup.py install

The setup.py command will install CIRpy in your `site-packages` folder so it is automatically available to all your
python scripts.

Option 3: Clone the repository
------------------------------

The latest development version of CIRpy is always `available on GitHub`_. This version is not guaranteed to be
stable, but may include new features that have not yet been released. Simply clone the repository and install as usual::

    git clone https://github.com/mcs07/CIRpy.git
    cd CIRpy
    python setup.py install

.. _`install it using get-pip.py`: http://www.pip-installer.org/en/latest/installing.html
.. _`download the latest release`: https://github.com/mcs07/CIRpy/releases/
.. _`available on GitHub`: https://github.com/mcs07/CIRpy
