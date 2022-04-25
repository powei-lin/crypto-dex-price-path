from scipy.optimize import least_squares


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


def swap2(a_0, b_0, b_1, b_2, b_3, w_0, w_1, w_2, w_3, f_0, f_1):
    return (
        b_1
        * b_3
        * f_0
        * f_1
        * w_0
        * w_2
        * (b_0 / (a_0 * f_0 + b_0)) ** (w_0 / w_1)
        * (b_2 / (b_1 * f_1 * (1 - (b_0 / (a_0 * f_0 + b_0)) ** (w_0 / w_1)) + b_2))
        ** (w_2 / w_3)
        / (
            w_1
            * w_3
            * (a_0 * f_0 + b_0)
            * (b_1 * f_1 * (1 - (b_0 / (a_0 * f_0 + b_0)) ** (w_0 / w_1)) + b_2)
        )
        - 1
    )


def calculate_max_profit(path):

    pass


def find_arb_path(path_list: list, pool_dict: dict):
    max_s, max_path = 1.0, None
    for path in path_list:
        s = 1.0
        for d in path:
            tk0, tk1 = d["token_in"], d["token_out"]
            s *= pool_dict[d["pool_addr"]].slope(tk0, tk1)
        if s > max_s:
            max_s = s
            max_path = path
    return max_s, max_path
