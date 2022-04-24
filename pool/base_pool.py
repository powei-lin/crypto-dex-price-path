class BasePool:
    def __init__(self, _addr: str, _tokens: list, _weights: list, _fee: float):

        self.addr = _addr
        self.tokens = _tokens
        self.weight = _weights
        self.fee = _fee
