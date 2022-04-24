class BasePool:
    def __init__(self, _addr: str, _tokens: list, _weights: list, _fee: float):

        self.addr = _addr
        self.tokens = set(_tokens)
        self.token_weights = {t: w for t, w in zip(_tokens, _weights)}
        self.fee = _fee
        self.token_balances = {t: 0 for t in _tokens}

    async def update_async(self):
        self.fee += 1
