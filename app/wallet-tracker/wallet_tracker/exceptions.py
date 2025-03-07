class NotSwapTransaction(Exception):
    pass


class TransactionError(Exception):
    pass


class TooManyRequests(Exception):
    pass


class UnknownTransactionType(Exception):
    pass


class ZeroChangeAmountError(Exception):
    def __init__(self, pre_amount: int, post_amount: int):
        self.pre_amount = pre_amount
        self.post_amount = post_amount

    def __str__(self):
        return f"Pre amount: {self.pre_amount}, Post amount: {self.post_amount}"
