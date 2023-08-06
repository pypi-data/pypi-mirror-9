piecash
=======

|build-status| |docs|

Piecash provides a simple and pythonic interface to GnuCash files stored in SQL (sqlite3 and Postgres, not tested in MySQL).

:Documentation: http://piecash.readthedocs.org.
:Google group: https://groups.google.com/d/forum/piecash (piecash@googlegroups.com)
:Github: https://github.com/sdementen/piecash


It is a pure python package, tested on python 2.7 and 3.4, that can be used as an alternative to:

- the official python bindings (as long as no advanced book modifications and/or engine calculations are needed).
  This is specially useful on Windows where the official python bindings may be tricky to install or if you want to work with
  python 3.
- XML parsing/reading of XML GnuCash files if you prefer python over XML/XLST manipulations.

It allows you to:

- open existing GnuCash documents and access all objects within
- modify objects or add new objects (accounts, transactions, prices, ...)
- create new GnuCash documents from scratch

Scripts are also available to:

- export to ledger-cli format (http://www.ledger-cli.org/)
- export to QIF format


A simple example of a piecash script:

.. code-block:: python

    with open_book("example.gnucash") as book:
        # get default currency of book
        print( book.default_currency )  # ==> Commodity<CURRENCY:EUR>

        # iterating over all splits in all books and print the transaction description:
        for acc in book.accounts:
            for sp in acc.splits:
                print(sp.transaction.description)

The project has reached beta stage.

.. warning::

   1) Always do a backup of your gnucash file/DB before using piecash.
   2) Test first your script by opening your file in readonly mode (which is the default mode)



.. |build-status| image:: https://travis-ci.org/sdementen/piecash.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/sdementen/piecash

.. |docs| image:: https://readthedocs.org/projects/piecash/badge/?version=master
    :alt: Documentation Status
    :scale: 100%
    :target: http://piecash.readthedocs.org

