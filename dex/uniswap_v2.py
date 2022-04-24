import asyncio
from web3 import Web3
from web3constant.abi.UniswapV2 import (
    UNISWAP_V2_ROUTER_ABI,
    UNISWAP_V2_PAIR_ABI,
    UNISWAP_V2_FACTORY_ABI,
)


def create_contract(network, address: str, abi: str):
    return network.eth.contract(address=address, abi=abi)


class UniSwap_v2:
    def __init__(self, network, factory_address, router_address) -> None:
        self.network = network
        self.factory_address = Web3.toChecksumAddress(factory_address)
        self.router_address = Web3.toChecksumAddress(router_address)
        self.factory = self.factory_contract()
        self.router = self.router_contract()

    def fee_10000(self) -> int:
        return 9970

    def get_amount(self, token0_Wei, token0_address, token1_address):
        try:
            return self.router.functions.getAmountsOut(
                token0_Wei, (token0_address, token1_address)
            ).call()[1]
        except:
            return 0

    def getAmountsOut(self, token0_Wei, token0_address, token1_address):
        return self.router.functions.getAmountsOut(
            token0_Wei, (token0_address, token1_address)
        ).call()

    def getPair(self, token0_address, token1_address):
        return self.factory.functions.getPair(token0_address, token1_address).call()

    def factory_all_pairs_length(self):
        return self.factory.functions.allPairsLength().call()

    def factory_all_pairs(self, idx: int):
        return self.factory.functions.allPairs(idx).call()

    def router_abi(self):
        return UNISWAP_V2_ROUTER_ABI

    def factory_abi(self):
        return UNISWAP_V2_FACTORY_ABI

    def factory_contract(self):
        return self.network.eth.contract(
            address=self.factory_address, abi=self.factory_abi()
        )

    def router_contract(self):
        return self.network.eth.contract(
            address=self.router_address, abi=self.router_abi()
        )

    """ async """

    async def factory_all_pairs_async(self, idx: int):
        return await self.factory.functions.allPairs(idx).call()

    async def getPairAsync(self, token0_address, token1_address):
        return await self.factory.functions.getPair(
            token0_address, token1_address
        ).call()

    async def getReservesAsync(self, token0_address, token1_address):
        pair_address = await asyncio.create_task(
            self.getPairAsync(token0_address, token1_address)
        )
        if pair_address == "0x0000000000000000000000000000000000000000":
            return 0, 0
        pair_contract = create_contract(self.network, pair_address, UNISWAP_V2_PAIR_ABI)
        token0 = await pair_contract.functions.token0().call()
        reserves = await pair_contract.functions.getReserves().call()
        if token0 != token0_address:
            return reserves[1], reserves[0]
        return reserves[0], reserves[1]

    async def get_amount_async(self, token0_Wei, token0_address, token1_address):
        try:
            return (
                await self.router.functions.getAmountsOut(
                    token0_Wei, (token0_address, token1_address)
                ).call()
            )[1]
        except:
            return 0
