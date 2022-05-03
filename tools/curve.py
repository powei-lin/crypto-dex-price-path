import asyncio
from web3abi.Curve import (
    CURVE_TRICRYPTO_ABI,
    CURVE_TRICRYPTO_MATH_ABI,
    CURVE_TRICRYPTO_VIEW_ABI,
)
from .util import create_contract


def creat_tricrypto_contract(w3):
    curve_3_coin_address = "0x3a1659Ddcf2339Be3aeA159cA010979FB49155FF"
    return create_contract(w3, curve_3_coin_address, CURVE_TRICRYPTO_ABI)


def create_tricrypto_math_contract(w3):
    curve_math_address = "0x939986418baFb4E2d82A76E320767Ff02d250203"
    return create_contract(w3, curve_math_address, CURVE_TRICRYPTO_MATH_ABI)


def create_tricrypto_view_contract(w3):
    curve_view_address = "0x4643A6600eae4851677A1f16d5e40Ef868c71717"
    return create_contract(w3, curve_view_address, CURVE_TRICRYPTO_VIEW_ABI)


async def get_amount(
    curve_tricrypto_contract, amount_in_wei: int, token_in_idx: int, token_out_idx: int
):
    dy = await curve_tricrypto_contract.functions.get_dy(
        token_in_idx, token_out_idx, amount_in_wei
    ).call()
    return dy


async def get_tricrypto_params(curve_tricrypto_contract):
    d = {}

    params = await asyncio.gather(
        curve_tricrypto_contract.functions.price_scale(0).call(),
        curve_tricrypto_contract.functions.price_scale(1).call(),
        curve_tricrypto_contract.functions.balances(0).call(),
        curve_tricrypto_contract.functions.balances(1).call(),
        curve_tricrypto_contract.functions.balances(2).call(),
        curve_tricrypto_contract.functions.D().call(),
    )

    d["gamma"] = 21000000000000
    d["A"] = 540000
    d["precisions"] = [
        1000000000000,
        10000000000,
        1,
    ]
    d["price_scale"] = params[:2]
    d["xp"] = params[2:5]
    d["D"] = params[5]
    d["P"] = 1e18
    d["N"] = 3
    return d


def scale_xp(xp, precisions, price_scale, PRECISION=1e18, N_COINS=3):
    xp[0] *= precisions[0]
    for k in range(N_COINS - 1):
        xp[k + 1] = int(xp[k + 1] * price_scale[k] * precisions[k + 1] / PRECISION)
    return xp
