Supported Platforms
-------------------

- Windows 7
- Windows 8
- Ubuntu 14.10

Dependencies
------------

* `Python <https://www.python.org/downloads/>`_
* `Swig <http://www.swig.org/download.html>`_
* `Microsoft Visual C++ Compiler for Python 2.7 <http://aka.ms/vcpython27>`_

Install
-------

.. code:: bash

    pip install pocketsphinx

or
--

.. code:: bash

    git clone https://github.com/bambocher/pocketsphinx-python.git
    cd pocketsphinx-python
    python setup.py install

Import
------

.. code:: python

    try:
        # Python 2.x
        from sphinxbase import Config
        from pocketsphinx import Decoder
    except ImportError:
        # Python 3.x
        from sphinxbase.sphinxbase import Config
        from pocketsphinx.pocketsphinx import Decoder


