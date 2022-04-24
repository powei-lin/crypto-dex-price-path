from itertools import combinations
import asyncio
from web3constant.abi.UniswapV2 import UNISWAP_V2_PAIR_ABI

import sys

sys.path.append("..")  # Adds higher directory to python modules path.
from pool.base_pool import BasePool
import dex


def all_dexes_objs(w3):
    dex_names = dir(dex)
    dex_names = dex_names[: dex_names.index("__builtins__")]
    return [getattr(dex, dex_name)(w3) for dex_name in dex_names]


async def get_pool_addr(dex_obj, token0, token1):
    pool_addr = await dex_obj.getPair(token0, token1)
    if pool_addr == "0x0000000000000000000000000000000000000000":
        return None
    return pool_addr


async def get_pool_from_dex(dex_obj, token0, token1):
    pool_addr = await get_pool_addr(dex_obj, token0, token1)
    if not pool_addr:
        return None
    tk_list = []
    if token0.lower() < token1.lower():
        tk_list = [token0, token1]
    else:
        tk_list = [token1, token0]
    fee = 1 - dex_obj.fee_10000() / 10000
    # pair_contract = w3_async.eth.contract(
    #     address=pool_addr, abi=UNISWAP_V2_PAIR_ABI)

    return BasePool(pool_addr, tk_list, [1, 1], fee)


async def pair_from_availible_tokens(w3_async, availible_tokens: set):
    token_combination_list = list(combinations(availible_tokens, 2))
    dex_objs = all_dexes_objs(w3_async)
    tasks = []
    for dex_obj in dex_objs:
        for token0, token1 in token_combination_list:
            tasks.append(
                asyncio.create_task(get_pool_from_dex(dex_obj, token0, token1))
            )
    pool_addr_dict = {}
    for task in tasks:
        pool_obj = await task
        if pool_obj:
            addr = pool_obj.addr
            pool_addr_dict[addr] = pool_obj
    return pool_addr_dict


# async def get_token_combination_pair_contract(dexes, all_token_addresses,
#                                               network):
#     # record for estimating performance
#     start_time_stamp = perf_counter()

#     combination_list = list(combinations(all_token_addresses, 2))
#     result = []
#     fail_count = 0

#     # print("get pair: {0:.2f}%".format(i / pair_length * 100))
#     # pair_addresses = []
#     # for j in range(i, min(i + step, pair_length)):
#     #     pair_addresses.append(
#     #         asyncio.create_task(dex_swap.factory_all_pairs(j)))
#     combine_length = len(combination_list)
#     for dex_name, dex_obj in dexes:
#         step = 500
#         for i in range(0, combine_length, step):
#             pair_addresses_tasks = []
#             for tk0_addr, tk1_addr in combination_list[
#                     i:min(i + step, combine_length)]:
#                 # sort token address
#                 if (tk0_addr.lower() > tk1_addr.lower()):
#                     tk0_addr, tk1_addr = tk1_addr, tk0_addr
#                 pair_addresses_tasks.append(
#                     (dex_name,
#                      asyncio.create_task(
#                          dex_obj.getPairAsync(tk0_addr,
#                                               tk1_addr)), tk0_addr, tk1_addr))

#             for dex_name, pair_task, tk0_addr, tk1_addr in pair_addresses_tasks:
#                 try:
#                     pair_address = await pair_task
#                 except:
#                     fail_count += 1
#                     continue
#                 if (pair_address ==
#                         '0x0000000000000000000000000000000000000000'):
#                     continue
#                 pair_contract = network.eth.contract(
#                     address=pair_address, abi=constant.UNISWAP_V2_PAIR_ABI)
#                 result.append((dex_name, pair_contract, tk0_addr, tk1_addr))

#     duration_second = perf_counter() - start_time_stamp
#     print("fail/total:", fail_count, len(pair_addresses_tasks))
#     print("Created {0} pairs using {1:.3f} seconds.".format(
#         len(result), duration_second))

#     return result
