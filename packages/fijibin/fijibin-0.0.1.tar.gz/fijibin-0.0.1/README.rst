fijibin
=======

This software will download the latest *Life-Line* version of
`Fiji <http://fiji.sc/>`__ and make the binary easily available from
python.

Current Fiji Life-Line version in this package is **2014 November 25**.

Install
-------

::

    pip install fijibin

Use
---

.. code:: python

    >>> import fijibin
    >>> fijibin.BIN
    '/Users/arve/.bin/Fiji.app/Contents/MacOS/ImageJ-macosx'
    >>> fijibin.VERSION
    '0.0.1'
    >>> fijibin.FIJI_VERSION
    '20141125'

``fijibin.BIN`` will point to linux, mac or windows version, depending
on the operating system detected via
`platform <https://docs.python.org/3.4/library/platform.html>`__.

Refetch binary
--------------

.. code:: python

    >>> from fijibin.fetch import fetch
    >>> fetch()

