from .uniswap_v2 import UniSwap_v2


class SwapTemplate(UniSwap_v2):
    def __init__(self, network) -> None:
        factory_address = ""
        router_address = ""
        super().__init__(network, factory_address, router_address)

    def fee_10000(self) -> int:
        return 9980
