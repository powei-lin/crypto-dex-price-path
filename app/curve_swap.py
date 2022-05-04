import sys
import asyncio
from itertools import repeat
from multiprocessing.pool import ThreadPool
from time import perf_counter, sleep
from web3 import Web3
from web3constant.Fantom.Url import FTM_RPC
from web3constant.Fantom.ERC20_address import WFTM, USDC

sys.path.append(".")
from tools import beethovenX, util, uniswap_dex, optimizer, curve


async def main():
    w3_async = util.create_async_w3(FTM_RPC)
    if await w3_async.isConnected():
        print("Web3 is connected")
    else:
        print("Connection Fail")
        return

    token_name_dict = util.load_json("data/top_tokens_ftm.json")
    available_tokens = set(curve.CURVE_TOKENS + [WFTM])

    uni_pair_dict = await uniswap_dex.pair_from_availible_tokens(
        w3_async, available_tokens
    )

    curve_tricrypto_contract = curve.creat_tricrypto_contract(w3_async)

    paths = optimizer.build_path_with_curve(
        uni_pair_dict, curve.CURVE_TRICRYPTO_ADDRESS
    )

    while True:
        tricrypto_params, _ = await asyncio.gather(
            curve.get_tricrypto_params(curve_tricrypto_contract),
            util.update_pool_dict(uni_pair_dict, False),
        )

        amount_in = Web3.toWei(10, "ether")
        best = (0, None)
        s = perf_counter()

        for path in paths:
            amount_out = optimizer.amount_out_with_path_curve(
                path, uni_pair_dict, tricrypto_params, amount_in
            )
            if amount_out / amount_in > best[0]:
                best = amount_out / amount_in, [
                    token_name_dict[d["token_in"]] for d in path
                ]
        duration = perf_counter() - s
        print("\n", best)
        print("calculate best path: {0:.6f} sec".format(duration))
    #     # print(await w3_async.eth.get_block_number())
    #     s = perf_counter()
    #     block_num, _ = await asyncio.gather(
    #         w3_async.eth.get_block_number(), util.update_pool_dict(combined_dict, False)
    #     )
    #     arbs = optimizer.find_arb_path(path_list, combined_dict)
    #     best_path = await optimizer.calculate_max_profit(arbs, combined_dict)
    #     print(perf_counter() - s)
    #     print(block_num)
    #     print(util.path_to_string(best_path, combined_dict, token_name_dict))
    # #


if __name__ == "__main__":
    asyncio.run(main())
