import sys
import asyncio
from web3constant.Fantom.Url import FTM_RPC

sys.path.append(".")
from tools import util


async def main():
    w3_async = util.create_async_w3(FTM_RPC)
    if await w3_async.isConnected():
        print("Web3 is connected")
    else:
        print("Connection Fail")
        return


if __name__ == "__main__":
    asyncio.run(main())
