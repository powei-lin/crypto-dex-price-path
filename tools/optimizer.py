def build_path_map(pool_dict: dict, start_token, max_hop: int):
    path_map = []

    def dfs(current_tk, prev_path, used_key: set, end_tk, remain_hop):
        for pool_key, pool_obj in pool_dict.items():
            if pool_key in used_key or current_tk not in pool_obj.tokens:
                continue
            for tk in pool_obj.tokens:
                if tk != current_tk:
                    current_path = prev_path + [(current_tk, pool_key)]
                    if tk == end_tk:
                        path_map.append(current_path)
                    elif remain_hop > 1:
                        used_copy = used_key.copy()
                        used_copy.add(pool_key)
                        dfs(tk, current_path, used_copy, end_tk, remain_hop - 1)

    dfs(start_token, [], set(), start_token, max_hop)

    return path_map
