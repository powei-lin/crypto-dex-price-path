from ..uniswap_v2 import UniSwap_v2
from web3constant.Fantom.Dex import (
    SUSHI_SWAP_FACTORY_ADDRESS,
    SUSHI_SWAP_ROUTER_ADDRESS,
)


class SushiSwap(UniSwap_v2):
    def __init__(self, network) -> None:
        factory_address = SUSHI_SWAP_FACTORY_ADDRESS
        router_address = SUSHI_SWAP_ROUTER_ADDRESS
        super().__init__(network, factory_address, router_address)

    def fee_10000(self) -> int:
        return 9970
