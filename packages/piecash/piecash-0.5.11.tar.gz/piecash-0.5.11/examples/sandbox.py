from __future__ import print_function
from decimal import Decimal
import datetime
import decimal
import inspect

from piecash import open_book, Transaction, Split, ScheduledTransaction, create_book, Budget
from piecash._common import Recurrence

with open_book("../gnucash_books/default_book.gnucash") as s:
    # accessing the book object from the session
    book = s.book

    # accessing root accounts
    root = book.root_account

    # accessing children accounts of root
    r = s.book.root_account.children(name="Assets").children[0]
    for acc in s.book.root_account.children(name="Assets").children[0].children:
        print(acc)

    print(inspect.getmro(Budget))
    print(inspect.getmro(Recurrence))
    b = Budget(name=lambda x:x, foo="3")
    b = Budget(name=lambda x:x, foo="3")
    fdsd
    print(b)
fdsfds


with create_book() as s:
    # retrieve list of slots
    print(s.book.slots)

    # set slots
    s.book["myintkey"] = 3
    s.book["mystrkey"] = "hello"
    s.book["myboolkey"] = True
    s.book["mydatekey"] = datetime.datetime.today().date()
    s.book["mydatetimekey"] = datetime.datetime.today()
    s.book["mynumerickey"] = decimal.Decimal("12.34567")
    s.book["account"] = s.book.root_account

    # iterate over all slots
    for k, v in s.book.iteritems():
        print("slot={v} has key={k} and value={v.value} of type {t}".format(k=k,v=v,t=type(v.value)))

    # delete a slot
    del s.book["myintkey"]
    # delete all slots
    del s.book[:]

    # create a key/value in a slot frames (and create them if they do not exist)
    s.book["options/Accounts/Use trading accounts"]="t"
    # access a slot in frame in whatever notations
    s1=s.book["options/Accounts/Use trading accounts"]
    s2=s.book["options"]["Accounts/Use trading accounts"]
    s3=s.book["options/Accounts"]["Use trading accounts"]
    s4=s.book["options"]["Accounts"]["Use trading accounts"]
    assert s1==s2==s3==s4

dsqdsq
with open_book("/home/sdementen/Desktop/test_sch_txn_sqlite.gnucash", acquire_lock=False, open_if_lock=True) as s:
    print(s.book.root_template.children)
    print(s.commodities)
    for tr in s.transactions:
        print(tr.splits[0].slots)
        print(tr.slots)
    print(s.transactions[0].scheduled_transaction)
    s.transactions[0].scheduled_transaction = None
    #print(s.transactions[0]["from-sched-xaction"])
    s.book["a/n"]
    print(s.accounts.get(name='Checking Account').lots.get(title="Lot 3"))
fdsfdssfd

dsqdsqdsq
with open_book("../gnucash_books/simple_sample.gnucash", acquire_lock=False, open_if_lock=True) as s:
    asset = s.accounts.get(name="Asset")
    expense = s.accounts.get(name="Expense")
    eur = asset.commodity
    tr = Transaction(currency=eur,
                     description="test",
                     splits=[Split(asset, 100), Split(expense, -100)])
    print(tr)
dffdsfsd

from piecash import open_book, create_book, Account, Transaction, Split

# with create_book("all_account_types.gnucash", overwrite=True) as s:
# for actype in ACCOUNT_TYPES:
#         if actype=="ROOT":
#             continue
#         acc = Account(name=actype, account_type=actype, parent=s.book.root_account, commodity=s.book.root_account.commodity)
#     s.save()

with open_book("simple_sample.gnucash", acquire_lock=False, open_if_lock=True) as s:
    asset = s.accounts.get(name="Asset")
    expense = s.accounts.get(name="Expense")
    eur = asset.commodity
    tr = Transaction(currency=eur,
                     description="test",
                     splits=[Split(asset, 100), Split(expense, -100)])
    print(tr)
    fdsdf
    for tr in s.transactions:
        for sp in tr.splits:
            sp.account = asset

    fdsfsdfd

    for tr in s.transactions:
        print(tr)
        for sp in tr.splits:
            print("\t", sp)

    for acc in s.accounts:
        if acc.commodity:
            print(acc.commodity.base_currency)
            bal = acc.get_balance()
            print("{} : {} {}".format(acc.fullname, bal, acc.commodity.mnemonic))

fsdsfsd


# with create_book("test_simple_transaction.gnucash",overwrite=True) as s:
with create_book(currency="EUR") as s:
    EUR = s.commodities.get(mnemonic="EUR")
    acc1 = Account(name="acc1",
                   commodity=EUR,
                   parent=s.book.root_account,
                   account_type="BANK")
    acc2 = Account(name="acc2",
                   commodity=EUR,
                   parent=s.book.root_account,
                   account_type="BANK",
                   commodity_scu=10)
    s.sa_session.flush()

    tr = Transaction(currency=EUR,
                     description="foo",
                     splits=[
                         Split(value=Decimal("1.2345"),
                               account=acc1),
                         Split(value=Decimal("-1.2345"),
                               account=acc2),
                     ])
    s.sa_session.flush()

    print([(sp._quantity_denom, sp._value_denom) for sp in tr.splits])
    print(s.sa_session.query(Account.commodity).all())
    print(tr.slots)
    tr.post_date = datetime.datetime.now()
    print(tr.slots)
    tr.post_date = None
    print(tr.slots)
    print(acc2.slots)
    acc2.placeholder = 1
    print(acc2.slots)
    acc2.placeholder = 0
    print(acc2.slots)
    s.save()
    # del tr.splits[-1]
    # print tr.get_imbalances()

dsqsdqdqs
#
# with create_book("test.gnucash", keep_foreign_keys=False, overwrite=True) as s:
# EUR = Commodity.create_from_ISO("EUR")
# tr = Transaction(currency=EUR,description="first")
#     sp = Split(transaction=tr, account=s.book.root_account, value=(100,1), quantity=(10,1))
#     tr = Transaction(currency=EUR,description="second")
#     s.save()


# with open_book("trading_accounts.gnucash", readonly=False) as s:
#     for tr in s.transactions:#.get(description="other transfer + expense")
#         print "{}\t{}".format(tr.currency, tr.description)
#         # print tr.get_imbalances()
#         for sp in tr.splits:
#             print "\t[{}] {} / {} for {}".format( sp.account.commodity,sp.value, sp.quantity,sp.account)
#     # tr1 = s.transactions.get(description="first")
#     # tr2 = s.transactions[1]
#     tr2 = s.transactions.get(description="cross CAD to USD transfer (initiated from USD account)")
#     sp = s.transactions.get(description="cross CAD to USD transfer").splits[0]
#     # sp = s.transactions[0].splits[0]
#     print "o"*100
#     # print sp
#     print "o"*100
#     sp.transaction = tr2
#     s.sa_session.flush()
# fdfdsfsd

with open_book("trading_accounts.gnucash", readonly=False, open_if_lock=True, acquire_lock=True) as s:
    for tr in s.transactions:  #.get(description="other transfer + expense")
        print("{}\t{}".format(tr.currency, tr.description))
        # print tr.get_imbalances()
        for sp in tr.splits:
            print("\t[{}] {} / {} for {}".format(sp.account.commodity, sp.value, sp.quantity, sp.account))
    # sp.memo = "foo"
    # tr.description = "foo"
    # s.sa_session.flush()

    tr = s.transactions.get(description="cross CAD to USD transfer (initiated from USD account)")
    sp = s.transactions.get(description="cross CAD to USD transfer").splits[0]
    # sp.transaction = tr
    tr.description = "foo"
    # tr.currency = s.commodities[-1]
    # print "foooooooooooooooooooooooooooooooo"
    # print sp.transaction, s.transactions.get(description="cross CAD to USD transfer").splits[1].transaction

    acc = s.accounts[0]
    assert isinstance(acc, Account)
    acc.commodity_scu = 1

    s.sa_session.flush()
    Transaction(currency=s.commodities.get(mnemonic="EUR"),
                description="foo",
                splits=[
                    Split(value=Decimal("1.2345"),
                          account=s.accounts[0]),
                    Split(value=Decimal("1.2345"),
                          account=s.accounts[1]),
                ])
    s.sa_session.flush()
    # del tr.splits[-1]
    # print tr.get_imbalances()
fdfsdfds



# s = create_book(postgres_conn="postgres://user:passwd@localhost/gnucash_book1", overwrite=True)
# s = create_book("test.gnucash",overwrite=True)

s = create_book("test.gnucash", overwrite=True)
# s = create_book()
EUR = Commodity.create_from_ISO("EUR")
CAD = Commodity.create_from_ISO("CAD")
USD = Commodity.create_from_ISO("USD")
# EUR.fraction = 100000
acc1 = Account(name="foo EUR", parent=s.book.root_account, account_type="ASSET", placeholder=False, commodity=EUR)
acc2 = Account(name="baz CAD", parent=s.book.root_account, account_type="STOCK", placeholder=False, commodity=CAD)
acc3 = Account(name="baz USD", parent=s.book.root_account, account_type="STOCK", placeholder=False, commodity=USD)
# acc1.commodity_scu = 1000
t = Transaction(description="foo",
                post_date=datetime.datetime.now(),
                enter_date=datetime.datetime.now(),
                currency=EUR)
Split(transaction=t,
      value=-25,
      quantity=-25,
      account=acc1)
Split(transaction=t,
      value=15,
      quantity=10,
      account=acc2)
Split(transaction=t,
      value=11,
      quantity=12,
      account=acc3)
print(t.splits)
imb = t.get_imbalances()
print(imb)
t.add_imbalance_splits()
s.save()
# print s.sa_session.query(Split).filter(Split.value_magic>=1.0).all()
ffdsfdd

# print t.splits[0].value_gnc, t.splits[0].value_denom, t.splits[0].value_num

print(s.book.root_account.children.append(Account(name="rool", account_type="ASSET", placeholder=False, commodity=EUR)))
s.save()
print(s.transactions.get)
print(s.accounts.get)
s.close()
# end_of_example


with open_book("sample1.gnucash", readonly=False, open_if_lock=True) as s1, open_book("sample2.gnucash") as s2:
    b1 = s1.book
    # s2 = open_book("sample2.gnucash")
    b2 = s2.book

    eur = s1.get(Commodity, mnemonic="EUR")

    b1.root_account["notes"] = "Hello world!"

    p = Price(currency=eur,
              commodity=eur,
              value=Decimal("4234.342"),
    )
    s1.sa_session.add(p)
    print(p.value)
    print(p.value_denom)
    print(p.value_num)

    with b1:
        print(get_active_session())
        with b2:
            print(get_active_session())
        print(get_active_session())

    with b1:
        acc = Account(name="foo")
    print(s1.sa_session.new)
