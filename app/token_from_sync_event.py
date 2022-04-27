import asyncio
import sys
from time import time
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
import json

from web3constant.Cronos import Url
from web3constant.topics import PAIR_SYNC
from web3constant.abi.UniswapV2 import UNISWAP_V2_PAIR_ABI

sys.path.append(".")
from tools import beethovenX, util, uniswap_dex, optimizer


async def main():

    rpc_endpoint = "https://mainnet.aurora.dev:443"
    w3_async = Web3(
        AsyncHTTPProvider(rpc_endpoint),
        modules={"eth": (AsyncEth,)},
        middlewares=[],
    )

    # chech if fantom network is connected
    if await w3_async.isConnected():
        print("Web3 is connected.")

    prev_block_num = await w3_async.eth.get_block_number()
    top_tokens = {}
    bad_tk = {}

    tokenset = set()
    while True:
        current_block = await w3_async.eth.get_block_number()
        if prev_block_num == current_block:
            continue
        print(current_block)

        topic_d = {"fromBlock": prev_block_num - 100, "topics": [PAIR_SYNC]}
        log = await w3_async.eth.get_logs(topic_d)
        prev_block_num = current_block
        tasks = []
        for l in log:
            pc_addr = l["address"]
            pc = w3_async.eth.contract(address=pc_addr, abi=UNISWAP_V2_PAIR_ABI)
            tasks.append(asyncio.create_task(pc.functions.token0().call()))
            tasks.append(asyncio.create_task(pc.functions.token1().call()))

        for t in tasks:
            tk = await t
            if tk not in top_tokens and tk not in bad_tk:

                tokenset.add(await t)
        if len(tokenset) > 0:
            break
    print(tokenset)
    d_path = "top_tokens_from_sync0.json"
    d = {}
    token_website = "https://aurorascan.dev/token/"
    for t in tokenset:
        name = util.get_token_name(token_website, t)
        print(t, name)
        d[t] = name
    with open(d_path, "w") as ofile:
        json.dump(d, ofile, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
