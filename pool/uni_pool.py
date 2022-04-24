from .base_pool import BasePool


class UniPool(BasePool):
    def __init__(
        self, _addr: str, _tokens: list, _weights: list, _fee: float, _contract
    ):
        super().__init__(_addr, _tokens, _weights, _fee)
        self.contract = _contract
        self.t0 = _tokens[0]
        self.t1 = _tokens[1]

    async def update_async(self):
        reserves = await self.contract.functions.getReserves().call()
        is_update = False
        if self.token_balances[self.t0] != reserves[0]:
            self.token_balances[self.t0] = reserves[0]
            self.token_balances[self.t1] = reserves[1]
            is_update = True
        return is_update
