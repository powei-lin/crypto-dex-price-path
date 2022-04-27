from ..uniswap_v2 import UniSwap_v2


class DfynExchange(UniSwap_v2):
    def __init__(self, network) -> None:
        factory_address = "0xd9820a17053d6314B20642E465a84Bf01a3D64f5"
        router_address = "0x2724B9497b2cF3325C6BE3ea430b3cec34B5Ef2d"
        super().__init__(network, factory_address, router_address)

    def fee_10000(self) -> int:
        return 9970
