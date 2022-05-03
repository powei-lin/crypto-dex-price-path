import asyncio
from web3abi.Curve import (
    CURVE_TRICRYPTO_ABI,
    CURVE_TRICRYPTO_MATH_ABI,
    CURVE_TRICRYPTO_VIEW_ABI,
)
from .util import create_contract

CURVE_TRICRYPTO_ADDRESS = "0x3a1659Ddcf2339Be3aeA159cA010979FB49155FF"
CURVE_MATH_ADDRESS = "0x939986418baFb4E2d82A76E320767Ff02d250203"
CURVE_VIEW_ADDRESS = "0x4643A6600eae4851677A1f16d5e40Ef868c71717"

CURVE_TOKENS = [
    "0x049d68029688eAbF473097a2fC38ef61633A3C7A",
    "0x321162Cd933E2Be498Cd2267a90534A804051b11",
    "0x74b23882a30290451A17c44f4F05243b6b58C76d",
]


def creat_tricrypto_contract(w3):
    return create_contract(w3, CURVE_TRICRYPTO_ADDRESS, CURVE_TRICRYPTO_ABI)


def create_tricrypto_math_contract(w3):
    return create_contract(w3, CURVE_MATH_ADDRESS, CURVE_TRICRYPTO_MATH_ABI)


def create_tricrypto_view_contract(w3):
    return create_contract(w3, CURVE_VIEW_ADDRESS, CURVE_TRICRYPTO_VIEW_ABI)


async def get_amount(
    curve_tricrypto_contract, amount_in_wei: int, token_in_idx: int, token_out_idx: int
):
    dy = await curve_tricrypto_contract.functions.get_dy(
        token_in_idx, token_out_idx, amount_in_wei
    ).call()
    return dy


def get_amount_from_params(
    tricrypto_params, amount_in_wei: int, token_in_idx: int, token_out_idx: int
) -> int:

    A = tricrypto_params["A"]
    gamma = tricrypto_params["gamma"]
    D = tricrypto_params["D"]
    # make copy
    xp = tricrypto_params["xp"][:]

    xp[token_in_idx] += amount_in_wei
    xp = scale_xp(xp, tricrypto_params["precisions"], tricrypto_params["price_scale"])

    y = newton_y(A, gamma, xp[:], D, token_out_idx)

    dy = xp[token_out_idx] - y - 1
    xp[token_out_idx] = y
    if token_out_idx > 0:
        dy = dy * 1e18 / tricrypto_params["price_scale"][token_out_idx - 1]
    dy /= tricrypto_params["precisions"][token_out_idx]

    xp_int = [int(_xp) for _xp in xp]
    fee = _fee(xp_int)
    dy -= fee * dy / 10**10
    return int(dy)


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
    d["address"] = curve_tricrypto_contract.address
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


def newton_y(ANN, gamma, x: list, D, out_idx) -> int:
    """
    Calculating x[i] given other balances x[0..N_COINS-1] and invariant D
    ANN = A * N**N
    """
    N_COINS = 3  # <- change
    A_MULTIPLIER = 10000

    MIN_GAMMA = 10**10
    MAX_GAMMA = 5 * 10**16

    MIN_A = N_COINS**N_COINS * A_MULTIPLIER / 100
    MAX_A = N_COINS**N_COINS * A_MULTIPLIER * 1000

    # Safety checks
    assert ANN > MIN_A - 1 and ANN < MAX_A + 1  # dev: unsafe values A
    assert gamma > MIN_GAMMA - 1 and gamma < MAX_GAMMA + 1  # dev: unsafe values gamma
    assert D > 10**17 - 1 and D < 10**15 * 10**18 + 1  # dev: unsafe values D
    for k in range(3):
        if k != out_idx:
            frac = int(x[k] * 10**18 / D)
            assert (frac > 10**16 - 1) and (
                frac < 10**20 + 1
            )  # dev: unsafe values x[i]

    y = int(D / N_COINS)
    K0_i = 10**18
    S_i = 0

    x_sorted = x
    x_sorted[out_idx] = 0
    x_sorted = sorted(x_sorted, reverse=True)  # From high to low

    convergence_limit = int(max(max(x_sorted[0] / 10**14, D / 10**14), 100))
    for i in range(2, N_COINS + 1):
        _x = x_sorted[N_COINS - i]
        y = int(y * D / (_x * N_COINS))  # Small _x first
        S_i += _x
    for i in range(N_COINS - 1):
        K0_i = int(K0_i * x_sorted[i] * N_COINS / D)  # Large _x first

    for _ in range(255):
        y_prev = y

        K0 = int(K0_i * y * N_COINS / D)
        S = S_i + y  # sum of x_vec

        _g1k0 = gamma + 10**18
        if _g1k0 > K0:
            _g1k0 = _g1k0 - K0 + 1
        else:
            _g1k0 = K0 - _g1k0 + 1

        # D / (A * N**N) * _g1k0**2 / gamma**2
        mul1 = int(10**18 * D / gamma * _g1k0 / gamma * _g1k0 * A_MULTIPLIER / ANN)

        # 2*K0 / _g1k0
        mul2 = int(10**18 + (2 * 10**18) * K0 / _g1k0)

        yfprime = 10**18 * y + S * mul2 + mul1
        _dyfprime = D * mul2
        if yfprime < _dyfprime:
            y = int(y_prev / 2)
            continue
        else:
            yfprime -= _dyfprime
        fprime = int(yfprime / y)

        # y -= f / f_prime
        # y = (y * fprime - f) / fprime
        # y = (yfprime + 10**18 * D - 10**18 * S) // fprime + mul1 // fprime * (10**18 - K0) // K0
        y_minus = int(mul1 / fprime)
        y_plus = int((yfprime + 10**18 * D) / fprime + y_minus * 10**18 / K0)
        y_minus += 10**18 * S / fprime

        if y_plus < y_minus:
            y = int(y_prev / 2)
        else:
            y = y_plus - y_minus

        diff = 0
        if y > y_prev:
            diff = y - y_prev
        else:
            diff = y_prev - y
        if diff < max(convergence_limit, y / 10**14):
            frac = int(y * 10**18 / D)
            assert (frac > 10**16 - 1) and (
                frac < 10**20 + 1
            )  # dev: unsafe value for y
            return int(y)

    raise "Did not converge"


def reduction_coefficient(x: list, fee_gamma) -> int:
    """
    fee_gamma / (fee_gamma + (1 - K))
    where
    K = prod(x) / (sum(x) / N)**N
    (all normalized to 1e18)
    """
    K = 10**18
    S = 0
    for x_i in x:
        S += x_i
    N_COINS = len(x)
    # Could be good to pre-sort x, but it is used only for dynamic fee,
    # so that is not so important
    for x_i in x:
        K = K * N_COINS * x_i / S
    if fee_gamma > 0:
        K = fee_gamma * 10**18 / (fee_gamma + 10**18 - K)
    return K


def _fee(xp):
    fee_gamma = 500000000000000
    mid_fee = 11000000
    out_fee = 45000000
    f = reduction_coefficient(xp, fee_gamma)
    return (mid_fee * f + out_fee * (10**18 - f)) / 10**18
