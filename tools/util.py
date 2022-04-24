import json
import asyncio
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool


def create_async_w3(rpc_endpoint):
    return Web3(
        AsyncHTTPProvider(rpc_endpoint),
        modules={
            "eth": (AsyncEth,),
            "net": (AsyncNet,),
            "geth": (Geth, {"txpool": (AsyncGethTxPool,)}),
        },
        middlewares=[],
    )


def load_json(file_path):
    with open(file_path, "r") as ifile:
        d = json.load(ifile)
    return d


def create_contract(w3, address, abi):
    return w3.eth.contract(address=address, abi=abi)


async def update_pool_dict(pool_dict: dict, show_debug=True):
    tasks = []
    for pool in pool_dict.values():
        tasks.append(asyncio.create_task(pool.update_async()))
    count, total = 0, 0
    for task in tasks:
        if await task:
            count += 1
        total += 1
    if show_debug:
        print(count, total)
