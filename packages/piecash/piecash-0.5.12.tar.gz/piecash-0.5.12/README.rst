piecash
=======

|build-status| |docs|

piecash offers a pythonic interface to GnuCash documents stored through the SQL backend (sqlite, postgres).

A simple example:

.. code:: python

    from piecash import open_book

    # open a book and print all transactions to screen
    with open_book("test_cur.gnucash") as s:
        for tr in s.transactions:
            print("Transaction : {}".format(tr.description))
            for i, sp in enumerate(tr.splits):
                direction = "increased" if sp.value > 0 else "decreased"
                print("\t{} : '{}' is {} by {}".format(i,
                                                       sp.account.fullname,
                                                       direction,
                                                       sp.value))

    from piecash import create_book, Account
    # create a new account
    with create_book("my_new_book.gnucash") as s:
        acc = Account(name="Income", parent=s.book.root_account, type="INCOME")
        s.save()

The project documentation is available on http://piecash.readthedocs.org.


.. |build-status| image:: https://travis-ci.org/sdementen/piecash.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/sdementen/piecash

.. |docs| image:: https://readthedocs.org/projects/piecash/badge/?version=master
    :alt: Documentation Status
    :scale: 100%
    :target: http://piecash.readthedocs.org

