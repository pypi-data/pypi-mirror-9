# -*- coding: utf-8 -*-
from builtins import object
import shutil
import os
import pytest

from piecash import Transaction, Commodity, open_book, create_book, Account
from piecash.kvp import Slot
from piecash._common import GnucashException
from piecash.core.session import Version, gnclock

from test_helper import file_template, file_for_test


@pytest.fixture
def session(request):
    s = create_book()
    return s

@pytest.fixture
def sa_session(request):
    s = create_book()
    return s.sa_session


@pytest.fixture
def session_readonly(request):
    shutil.copyfile(file_template, file_for_test)

    # default session is readonly
    s = open_book(file_for_test)

    request.addfinalizer(lambda: os.remove(file_for_test))
    return s

@pytest.fixture
def session_readonly_lock(request):
    shutil.copyfile(file_template, file_for_test)

    # default session is readonly
    s = open_book(file_for_test, acquire_lock=True)

    def close_s():
        s.close()
        os.remove(file_for_test)
    request.addfinalizer(close_s)
    return s


class TestModelCore_EmptyBook(object):
    def test_accounts(self, session):
        # two accounts in an empty gnucash file
        account_names = session.query(Account.name).all()

        assert set(account_names) == {(u'Template Root',),
                                      (u'Root Account',),
        }

    def test_transactions(self, session):
        # no transactions in an empty gnucash file
        transactions = session.query(Transaction).all()
        assert transactions == []

    def test_commodities(self, session):
        # no commodities in an empty gnucash file
        commodities = session.query(Commodity.mnemonic).all()
        assert commodities == [("EUR",)]

    def test_slots(self, session):
        # no slots  in an empty gnucash file
        slots = session.query(Slot).all()
        assert slots == []

    def test_versions(self, session):
        # confirm versions of tables
        versions = session.query(Version.name,
                                 Version.version).all()
        assert set(versions) == {(u'Gnucash', 2060400), (u'Gnucash-Resave', 19920),
                                 (u'accounts', 1), (u'books', 1),
                                 (u'budgets', 1), (u'budget_amounts', 1), ('jobs', 1), (u'orders', 1),
                                 (u'taxtables', 2), (u'taxtable_entries', 3), (u'vendors', 1), (u'recurrences', 2),
                                 (u'slots', 3), (u'transactions', 3), (u'splits', 4), (u'lots', 2), (u'entries', 3),
                                 (u'billterms', 2), (u'invoices', 3), (u'commodities', 1), (u'schedxactions', 1),
                                 (u'prices', 2), (u'customers', 2), (u'employees', 2),
        }

    def test_readonly_true(self, session_readonly):
        # control exception when adding object to readonly gnucash db
        v = Version(name="sample", version="other sample")
        sa_session_readonly = session_readonly.sa_session
        sa_session_readonly.add(v)
        with pytest.raises(GnucashException):
            sa_session_readonly.commit()

        # control exception when deleting object to readonly gnucash db
        sa_session_readonly.delete(session_readonly.query(Account).first())
        with pytest.raises(GnucashException):
            sa_session_readonly.commit()

        # control exception when modifying object to readonly gnucash db
        sa_session_readonly.query(Account).first().name = "foo"
        with pytest.raises(GnucashException):
            sa_session_readonly.commit()


    def test_readonly_false(self, sa_session):
        v = Version(name="fo", version="ok")
        sa_session.add(v)
        assert sa_session.flush() is None

    def test_lock(self, session_readonly_lock):
        # test that lock is not taken in readonly session
        locks = list(session_readonly_lock.sa_session.execute(gnclock.select()))
        assert len(locks) == 0


# class TestModelCore_CreateObjects(object):
#     def test_accounts(self, session):
#         # two accounts in an empty gnucash file
#         # Account(type=)
#         account_names = session.query(Account.name).all()
#
#         assert set(account_names) == {(u'Template Root',),
#                                       (u'Root Account',),
#         }
#
#     def test_transactions(self, session):
#         # no transactions in an empty gnucash file
#         transactions = session.query(Transaction).all()
#         assert transactions == []
#
#     def test_commodities(self, session):
#         # no commodities  in an empty gnucash file
#         commodities = session.query(Commodity).all()
#         assert commodities == []
#
#     def test_slots(self, session):
#         # no slots  in an empty gnucash file
#         slots = session.query(Slot).all()
#         assert slots == []
#
#     def test_versions(self, session):
#         # confirm versions of tables
#         versions = session.query(Version.table_name,
#                                  Version.table_version).all()
#         assert set(versions) == {(u'Gnucash', 2060400), (u'Gnucash-Resave', 19920),
#                                  (u'accounts', 1), (u'books', 1),
#                                  (u'budgets', 1), (u'budget_amounts', 1), ('jobs', 1), (u'orders', 1),
#                                  (u'taxtables', 2), (u'taxtable_entries', 3), (u'vendors', 1), (u'recurrences', 2),
#                                  (u'slots', 3), (u'transactions', 3), (u'splits', 4), (u'lots', 2), (u'entries', 3),
#                                  (u'billterms', 2), (u'invoices', 3), (u'commodities', 1), (u'schedxactions', 1),
#                                  (u'prices', 2), (u'customers', 2), (u'employees', 2),
#         }