from .base_pool import BasePool


class BalancerPool(BasePool):
    def __init__(
        self,
        _addr: str,
        _tokens: list,
        _weights: list,
        _fee: float,
        _pool_id: str,
        _vault_contract,
    ):
        super().__init__(_addr, _tokens, _weights, _fee)
        self.pool_id = _pool_id
        self.vault_contract = _vault_contract

    async def update_async(self):
        (
            tokens,
            balances,
            lastChangeBlock,
        ) = await self.vault_contract.functions.getPoolTokens(self.pool_id).call()
