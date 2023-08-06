from decimal import Decimal
from unittest import TestCase

from .communication import ScratchApi, ScratchException, StartTransaction, CompleteTransaction
from .transaction import Purchase, Subscription, MultiTransaction

class ScratchTests(TestCase):
    def test_simple_api(self):
        result = ScratchApi("keys/check/").get()
        self.assertEqual(result.status_code, 200)
    
    def test_json(self):
        result = ScratchApi("keys/check/").get()
        self.assertEqual(type(result.json()), dict)
    
    def test_wrong_key(self):
        with self.assertRaises(ScratchException):
            ScratchApi("keys/check/", api_key="wrong").get()
    
    def test_wrong_secret(self):
        with self.assertRaises(ScratchException):
            ScratchApi("keys/check/", secret="wrong").get()

class TransactionTests(TestCase):
    def test_start(self):
        transaction = Purchase(amount=Decimal("1.5"), description="Testing purchase")
        redirect = "http://example.com/landing/"
        result = StartTransaction().post(redirect, transaction)
        keys = list(result.keys())
        self.assertIn("transaction", keys)
        self.assertIn("location", keys)
    
    def test_storage(self):
        storage = {}
        transaction = Purchase(amount=Decimal("1.5"), description="Testing purchase")
        redirect = "http://example.com/landing/"
        result = StartTransaction(storage).post(redirect, transaction)
        self.assertEqual(list(storage.values()), [False])
    
    def test_subscription(self):
        transaction = Subscription(
            amount = 2,
            interval = "monthly",
            description = "Donation to Scratch",
            product = "python",
            payments = 0,
        )
    
    def test_multiple(self):
        orgs = ["Scratch", "Python", "PyPI", "GitHub"]
        transaction = MultiTransaction([Subscription(
            amount = "1.%02d" % n,
            interval = "%d weeks" % (n+1),
            description = "Donation to " + org,
            product = org,
            payments = n,
        ) for n, org in enumerate(orgs)])
        redirect = "http://example.com/landing/"
        result = StartTransaction().post(redirect, transaction)
        self.assertIn("location", result)
    
    def test_complete_bogus(self):
        # A made up transaction identifier shouldn't succeed.
        result = CompleteTransaction().get("python")
        self.assertIsNone(result)
    
    def test_incomplete(self):
        # Incomplete transactions come back as false.
        transaction = Purchase(amount=Decimal("1.5"), description="Testing purchase")
        redirect = "http://example.com/landing/"
        started = StartTransaction().post(redirect, transaction)
        result = CompleteTransaction().get(started["transaction"])
        self.assertIsNone(result)
