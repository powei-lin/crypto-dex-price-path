import json
import requests
from bs4 import BeautifulSoup
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
    return True


def path_to_string(path, pool_dict: dict, token_name_dict: dict):
    st = ""
    for d in path:
        tk, pool_addr = d["token_in"], d["pool_addr"]
        st += token_name_dict[tk] + " -> " + pool_addr[:5] + " -> "
    st += token_name_dict[path[0]["token_in"]]
    return st


def print_path_list(path_list, combined_dict, token_name_dict):
    for path in path_list:
        print(path_to_string(path, combined_dict, token_name_dict))


def get_token_name(ftm_scan_token_url, token_address):
    res = requests.get(ftm_scan_token_url + token_address)
    soup = BeautifulSoup(res.text, "lxml")
    res = soup.find("span", {"class": "text-secondary small"})
    token_name = "NotFound"
    if res:
        token_name = res.getText()
    return token_name
