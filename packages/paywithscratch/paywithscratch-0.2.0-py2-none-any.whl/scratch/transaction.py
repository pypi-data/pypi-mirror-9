from decimal import Decimal
from json import dumps as json_encode

class Transaction(object):
    transaction_type = None
    
    def __init__(self):
        self.params = {
            "type": self.transaction_type,
        }

class Purchase(Transaction):
    transaction_type = "simple"
    
    def __init__(self, amount, description, currency="USD", product=None, **kwargs):
        super(Purchase, self).__init__(**kwargs)
        self.params["amount"] = str(Decimal(amount))
        self.params["currency"] = currency
        self.params["description"] = description
        self.params["product"] = product

class Subscription(Purchase):
    transaction_type = "subscription"
    
    def __init__(self, product, interval, payments=None, **kwargs):
        super(Subscription, self).__init__(**kwargs)
        self.params["product"] = product
        self.params["interval"] = interval
        if payments:
            self.params["payments"] = int(payments)

class MultiTransaction(Transaction):
    transaction_type = "multiple"
    
    def __init__(self, purchases, **kwargs):
        super(MultiTransaction, self).__init__(**kwargs)
        self.params["purchases"] = json_encode([transaction.params for transaction in purchases])
