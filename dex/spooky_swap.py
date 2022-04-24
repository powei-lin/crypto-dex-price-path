from .uniswap_v2 import UniSwap_v2


class SpookySwap(UniSwap_v2):
    def __init__(self, network) -> None:
        factory_address = "0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3"
        router_address = "0xF491e7B69E4244ad4002BC14e878a34207E38c29"
        super().__init__(network, factory_address, router_address)

    def fee_10000(self) -> int:
        return 9980


class SpookySwap_testnet(UniSwap_v2):
    def __init__(self, network) -> None:
        factory_address = "0xEE4bC42157cf65291Ba2FE839AE127e3Cc76f741"
        router_address = "0xa6AD18C2aC47803E193F75c3677b14BF19B94883"
        super().__init__(network, factory_address, router_address)
