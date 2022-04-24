from .base_pool import BasePool


class UniPool(BasePool):
    def __init__(
        self, _addr: str, _tokens: list, _weights: list, _fee: float, _contract
    ):
        super().__init__(_addr, _tokens, _weights, _fee)
        self.contract = _contract
