import asyncio
from web3 import Web3
from web3constant.Fantom.Dex import BEETHOVEN_VAULT_ADDRESS
from web3constant.abi.BalancerV2 import (
    BEETHOVENX_VAULT_ABI,
    BEETHOVENX_WEIGHTED_POOL_2TOKENS_ABI,
    BEETHOVENX_WEIGHTED_POOL_ABI,
)
from .util import create_contract
import sys

sys.path.append("..")  # Adds higher directory to python modules path.
from pool.base_pool import BasePool


def creat_vault_contract(w3):
    return create_contract(w3, BEETHOVEN_VAULT_ADDRESS, BEETHOVENX_VAULT_ABI)


async def get_pool(beethoven_vault_contract, pool_id):
    (pool_addr, pool_type), (tokens, balances, lastChangeBlock,) = await asyncio.gather(
        beethoven_vault_contract.functions.getPool(pool_id).call(),
        beethoven_vault_contract.functions.getPoolTokens(pool_id).call(),
    )

    return pool_addr, pool_type, tokens, balances, lastChangeBlock


async def get_pool_weight_fee(w3_async, beethoven_vault_contract, pool_id):

    pool_addr, pool_type, tokens, balances, lastChangeBlock = await get_pool(
        beethoven_vault_contract, pool_id
    )

    pool_abi = BEETHOVENX_WEIGHTED_POOL_2TOKENS_ABI
    if pool_type == 1:
        pool_abi = BEETHOVENX_WEIGHTED_POOL_ABI
    weighted_pool_contract = w3_async.eth.contract(address=pool_addr, abi=pool_abi)
    weights, swapFeePercentage = await asyncio.gather(
        weighted_pool_contract.functions.getNormalizedWeights().call(),
        weighted_pool_contract.functions.getSwapFeePercentage().call(),
    )
    return pool_addr, pool_type, tokens, balances, weights, swapFeePercentage


async def get_pool_dict_async(w3_async, beethoven_pools_j, beethoven_vault_contract):
    pool_addr_dict = {}

    tasks0 = []

    for pool_id in beethoven_pools_j:
        # GENERAL, MINIMAL_SWAP_INFO, TWO_TOKEN }
        tasks0.append(
            asyncio.create_task(
                get_pool_weight_fee(w3_async, beethoven_vault_contract, pool_id)
            )
        )

    for task in tasks0:

        pool_addr, pool_type, tokens, balances, weights, swapFeePercentage = await task

        fee = 1 - float(Web3.fromWei(swapFeePercentage, "ether"))
        pool_obj = BasePool(pool_addr, tokens, weights, fee)
        pool_addr_dict[pool_addr] = pool_obj
    return pool_addr_dict


def tokens_from_beets_pool_dict(pool_addr_dict: dict):
    tokens = set()
    for pool_obj in pool_addr_dict.values():
        for token in pool_obj.tokens:
            tokens.add(token)
    return tokens
