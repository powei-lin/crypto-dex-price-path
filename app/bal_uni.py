import sys
import asyncio
from time import perf_counter
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

    token_name_dict = util.load_json("data/top_tokens_ftm.json")

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
    path_list = optimizer.build_path_list(combined_dict, start_token=WFTM, max_hop=2)
    print(len(path_list))
    # return
    await util.update_pool_dict(combined_dict)

    slope, path = optimizer.find_arb_path(path_list, combined_dict)
    print(slope)
    optimizer.calculate_max_profit(path)
    print(util.path_to_string(path, combined_dict, token_name_dict))
    return
    while True:
        # print(await w3_async.eth.get_block_number())
        s = perf_counter()
        block_num, _ = await asyncio.gather(
            w3_async.eth.get_block_number(), util.update_pool_dict(combined_dict, False)
        )
        print(perf_counter() - s)
        print(block_num)
    #


if __name__ == "__main__":
    asyncio.run(main())
