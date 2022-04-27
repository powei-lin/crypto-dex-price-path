from itertools import repeat
import asyncio
from time import perf_counter
from scipy.optimize import least_squares
import numpy as np
import matplotlib.pyplot as plt
from web3 import Web3
from .swap_math import *

from multiprocessing import Pool


def build_path_list(pool_dict: dict, start_token, max_hop: int):
    path_list = []

    def dfs(current_tk, prev_path, used_key: set, end_tk, remain_hop):
        for pool_key, pool_obj in pool_dict.items():
            if pool_key in used_key or current_tk not in pool_obj.tokens:
                continue
            for tk in pool_obj.tokens:
                if tk != current_tk:
                    current_path = prev_path + [
                        {"token_in": current_tk, "token_out": tk, "pool_addr": pool_key}
                    ]
                    if tk == end_tk:
                        path_list.append(current_path)
                    elif remain_hop > 1:
                        used_copy = used_key.copy()
                        used_copy.add(pool_key)
                        dfs(tk, current_path, used_copy, end_tk, remain_hop - 1)

    dfs(start_token, [], set(), start_token, max_hop)

    return path_list


def path_to_params_and_swap_func(path, pool_dict: dict):
    params = []
    for p in path:
        tk0, tk1 = p["token_in"], p["token_out"]
        pool = pool_dict[p["pool_addr"]]
        b0 = pool.token_balances[tk0]
        b1 = pool.token_balances[tk1]
        w0 = pool.token_weights[tk0]
        w1 = pool.token_weights[tk1]
        f = pool.fee
        params += [b0, b1, w0, w1, f]

    swap_profit_func = swap2_profit_ether
    swap_profit_da0_func = swap2_profit_ether_d_a0
    if len(path) == 3:
        swap_profit_func = swap3_profit_ether
        swap_profit_da0_func = swap3_profit_ether_d_a0

    return params, swap_profit_func, swap_profit_da0_func


async def path_to_profit(path, pool_dict):
    amont_in = 0.0001
    params, swap_profit_func, swap_profit_da0_func = path_to_params_and_swap_func(
        path, pool_dict
    )

    # quick check
    if swap_profit_func(1, *params) < 0:
        return None, None

    # s = perf_counter()
    res_lsq2 = least_squares(
        swap_profit_da0_func, amont_in, args=np.array(params, dtype=np.float64)
    )
    if res_lsq2.x == amont_in:
        return None, None

    profit_ether = swap_profit_func(res_lsq2.x[0], *params)
    x = res_lsq2.x[0]
    return profit_ether, x


async def calculate_max_profit(path_list, pool_dict: dict):

    best_profit = 0
    best_x = 0
    best_path = None

    tasks = []
    for path in path_list:
        tasks.append(asyncio.create_task(path_to_profit(path, pool_dict)))
    for task in tasks:
        profit_ether, x = await task
        if profit_ether and profit_ether > best_profit:
            best_profit = profit_ether
            best_x = x
            best_path = path

    print("best profit:", best_profit)
    # x = np.linspace(0, best_x * 1.5)
    # (
    #     best_params,
    #     best_swap_profit_func,
    #     best_swap_profit_da0_func,
    # ) = path_to_params_and_swap_func(best_path, pool_dict)
    # y0 = [best_swap_profit_func(a, *best_params) for a in x]
    # y1 = [best_swap_profit_da0_func(a, *best_params) for a in x]
    # plt.plot(x, y0, x, y1)
    # plt.show()
    return best_path


def find_arb_path(path_list: list, pool_dict: dict):
    q = []
    for path in path_list:
        s = 1.0
        for d in path:
            tk0, tk1 = d["token_in"], d["token_out"]
            s *= pool_dict[d["pool_addr"]].slope(tk0, tk1)
        if s > 1:
            q.append(path)
    return q
