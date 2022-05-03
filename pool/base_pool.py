class BasePool:
    def __init__(self, _addr: str, _tokens: list, _weights: list, _fee: float):

        self.addr = _addr
        self.tokens = set(_tokens)
        self.token_weights = {t: w for t, w in zip(_tokens, _weights)}
        self.fee = _fee
        self.token_balances = {t: 0 for t in _tokens}

    async def update_async(self):
        raise NotImplementedError

    def slope(self, from_tk, to_tk):
        b_0, b_1 = self.token_balances[from_tk], self.token_balances[to_tk]
        w_0, w_1 = self.token_weights[from_tk], self.token_weights[to_tk]
        f_0 = self.fee
        return b_1 * f_0 * w_0 / (w_1 * b_0)
