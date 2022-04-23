import asyncio
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool
from web3constant.Fantom.Url import FTM_RPC
from web3constant.Fantom.ERC20_address import WFTM
from web3constant.abi.BalancerV2 import (
    BEETHOVENX_VAULT_ABI,
    BEETHOVENX_WEIGHTED_POOL_2TOKENS_ABI,
)


async def main():
    rpc_endpoint = FTM_RPC

    w3 = Web3(
        AsyncHTTPProvider(rpc_endpoint),
        modules={
            "eth": (AsyncEth,),
            "net": (AsyncNet,),
            "geth": (Geth, {"txpool": (AsyncGethTxPool,)}),
        },
        middlewares=[],
    )
    if await w3.isConnected():
        print("Network connected.")
    else:
        print("Not connected.")
        return

    token_names = {WFTM: "WFTM", "0xF24Bcf4d1e507740041C9cFd2DddB29585aDCe1e": "BEETS"}

    pool_id_WFTM_BEETS = (
        "0xcde5a11a4acb4ee4c805352cec57e236bdbc3837000200000000000000000019"
    )
    beethoven_vault_address = "0x20dd72Ed959b6147912C2e529F0a0C651c33c9ce"
    beethoven_vault_contract = w3.eth.contract(
        address=beethoven_vault_address, abi=BEETHOVENX_VAULT_ABI
    )
    pool_addr, token_num = await beethoven_vault_contract.functions.getPool(
        pool_id_WFTM_BEETS
    ).call()
    print("Pool address: {}, token numbers: {}".format(pool_addr, token_num))

    (
        tokens,
        balances,
        lastChangeBlock,
    ) = await beethoven_vault_contract.functions.getPoolTokens(
        pool_id_WFTM_BEETS
    ).call()
    weighted_pool_contract = w3.eth.contract(
        address=pool_addr, abi=BEETHOVENX_WEIGHTED_POOL_2TOKENS_ABI
    )
    print("tokens:")
    print(tokens)
    print("names:")
    print([token_names[t] for t in tokens])
    print("balances:")
    print(balances)

    weights = await weighted_pool_contract.functions.getNormalizedWeights().call()
    print("Weights:")
    print(weights)

    my_addr = "0x0000000000000000000000000000000000000000"
    assets = tokens

    (
        logInvariant,
        logTotalSupply,
        oracleSampleCreationTimestamp,
        oracleIndex,
        oracleEnabled,
        swapFeePercentage,
    ) = await weighted_pool_contract.functions.getMiscData().call()
    print("logInvariant", logInvariant)
    print("logTotalSupply", logTotalSupply)
    print("oracleSampleCreationTimestamp", oracleSampleCreationTimestamp)
    print("oracleIndex", oracleIndex)
    print("swapFeePercentage", Web3.fromWei(swapFeePercentage, "ether"))
    fee = 1 - float(Web3.fromWei(swapFeePercentage, "ether"))

    print()

    am_in_wei = Web3.toWei(1, "ether")
    print("validate:")
    base = balances[0] / (balances[0] + am_in_wei * fee)
    base_exp = base ** (2 / 8)
    am_out_wei = int(balances[1] * (1 - base_exp))
    print("amount out calculated:", am_out_wei)

    # queryBatchSwap
    kind = 0
    swaps = [
        {
            "poolId": pool_id_WFTM_BEETS,
            "assetInIndex": 0,
            "assetOutIndex": 1,
            "amount": am_in_wei,
            "userData": bytes(),
        }
    ]
    #         from, isFromVault, to, isToVault
    funds = (my_addr, False, my_addr, False)

    result = await beethoven_vault_contract.functions.queryBatchSwap(
        kind, swaps, assets, funds
    ).call()

    print("amount out from query:", -result[1])
    print("diff", (am_out_wei + result[1]) / -result[1] * 100, "%")


if __name__ == "__main__":
    asyncio.run(main())
