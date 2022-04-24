import sys
import asyncio
from web3 import Web3
from web3constant.Fantom.Url import FTM_RPC
from web3constant.Fantom.ERC20_address import WFTM

sys.path.append(".")
from tools import beethovenX, util, uniswap_dex, optimizer


async def main():
    w3_async = util.create_async_w3(FTM_RPC)
    if await w3_async.isConnected():
        print("Web3 is connected")
    else:
        print("Connection Fail")
        return

    # creat beethovenX pools
    beethoven_pools_j = util.load_json("data/beethovenX_pool.json")
    beethoven_vault_contract = beethovenX.creat_vault_contract(w3_async)
    beets_pool_dict = await beethovenX.get_pool_dict_async(
        w3_async, beethoven_pools_j, beethoven_vault_contract
    )

    # get available tokens and create uni type pool
    available_tokens = beethovenX.tokens_from_beets_pool_dict(beets_pool_dict)
    uni_pair_dict = await uniswap_dex.pair_from_availible_tokens(
        w3_async, available_tokens
    )
    combined_dict = dict(beets_pool_dict, **uni_pair_dict)
    await util.update_pool_dict(combined_dict)
    for v in combined_dict.values():
        print(v.fee)
    return
    while True:
        print(await w3_async.eth.get_block_number())
    optimizer.build_path_map(combined_dict, start_token=WFTM)
    #


if __name__ == "__main__":
    asyncio.run(main())
