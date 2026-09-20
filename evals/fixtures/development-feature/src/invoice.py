from decimal import Decimal


class Invoice:
    def __init__(self, amounts):
        self.amounts = [Decimal(str(amount)) for amount in amounts]

    def total(self):
        return sum(self.amounts, Decimal("0"))
