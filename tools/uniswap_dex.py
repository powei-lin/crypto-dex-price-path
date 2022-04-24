from itertools import combinations
import asyncio
from regex import P
from web3 import Web3
from web3constant.abi.UniswapV2 import UNISWAP_V2_PAIR_ABI

import sys

sys.path.append("..")  # Adds higher directory to python modules path.
from pool.uni_pool import UniPool
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


async def get_pool_from_dex(w3_async, dex_obj, token0, token1):

    # check pool exist
    pool_addr = await get_pool_addr(dex_obj, token0, token1)
    if not pool_addr:
        return None

    # check min reserves
    pair_contract = w3_async.eth.contract(address=pool_addr, abi=UNISWAP_V2_PAIR_ABI)
    min_reserve = Web3.toWei(1, "ether")
    reserves = await pair_contract.functions.getReserves().call()
    if reserves[0] + reserves[1] < min_reserve:
        return None

    tk_list = []
    if token0.lower() < token1.lower():
        tk_list = [token0, token1]
    else:
        tk_list = [token1, token0]
    fee = dex_obj.fee_10000() / 10000

    return UniPool(pool_addr, tk_list, [int(5e17), int(5e17)], fee, pair_contract)


async def pair_from_availible_tokens(w3_async, availible_tokens: set):
    print("Start creating Uni pools")
    token_combination_list = list(combinations(availible_tokens, 2))
    dex_objs = all_dexes_objs(w3_async)
    tasks = []
    for dex_obj in dex_objs:
        for token0, token1 in token_combination_list:
            tasks.append(
                asyncio.create_task(
                    get_pool_from_dex(w3_async, dex_obj, token0, token1)
                )
            )
    pool_addr_dict = {}
    for task in tasks:
        pool_obj = await task
        if pool_obj:
            addr = pool_obj.addr
            pool_addr_dict[addr] = pool_obj
    return pool_addr_dict
