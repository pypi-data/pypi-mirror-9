fijibin
=======

This software will download the latest *Life-Line* version of
`Fiji <http://fiji.sc/>`__, make the correct cross-platform binary
available and provide a macro submodule which makes automation of Fiji
trivial from python.

**Video demo**

|image0|

Current Fiji Life-Line version in this package is **2014 November 25**.

If you experience any trouble with this module, please `submit an
issue <https://github.com/arve0/fijibin/issues/new>`__ or send a pull
request on github.

Install
-------

::

    pip install fijibin

Usage
-----

.. code:: python

    >>> import fijibin
    >>> fijibin.BIN
    '/Users/arve/.bin/Fiji.app/Contents/MacOS/ImageJ-macosx'
    >>> fijibin.FIJI_VERSION
    '20141125'

``fijibin.BIN`` will point to linux, mac or windows version, depending
on the operating system detected via
`platform <https://docs.python.org/3.4/library/platform.html>`__.

Macros
~~~~~~

.. code:: python

    import fijibin.macro
    macro.run(macro_string_or_list_of_strings)

Refetch binary
~~~~~~~~~~~~~~

.. code:: python

    >>> from fijibin.fetch import fetch
    >>> fetch()

See more in the `API reference <http://fijibin.readthedocs.org/>`__.

Development
-----------

Install dependencies and link development version of fijibin to pip:

.. code:: bash

    git clone https://github.com/arve0/fijibin
    cd fijibin
    pip install -r requirements.txt

run test
~~~~~~~~

.. code:: bash

    pip install tox
    tox

extra output, jump into pdb upon error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    DEBUG=fijibin tox -- --pdb -s

build api reference
~~~~~~~~~~~~~~~~~~~

.. code:: bash

    make docs

.. |image0| image:: http://img.youtube.com/vi/v0q88SisBtw/0.jpg
   :target: http://youtu.be/v0q88SisBtw
