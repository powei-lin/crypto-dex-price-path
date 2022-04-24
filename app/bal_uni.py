from lib2to3.pgen2 import token
import sys
import asyncio
from web3 import Web3
from web3constant.Fantom.Url import FTM_RPC

sys.path.append(".")
from tools import beethovenX, util
from pool.base_pool import BasePool


async def main():
    w3_async = util.create_async_w3(FTM_RPC)
    if await w3_async.isConnected():
        print("Web3 is connected")
    else:
        print("Connection Fail")
        return

    beethoven_pools_j = util.load_json("data/beethovenX_pool.json")
    beethoven_vault_contract = beethovenX.creat_vault_contract(w3_async)
    beets_pool_dict = await beethovenX.get_pool_dict_async(
        w3_async, beethoven_pools_j, beethoven_vault_contract
    )
    
    for pool_addr, pool_obj in beets_pool_dict.items():
        print(pool_obj.tokens)


if __name__ == "__main__":
    asyncio.run(main())
