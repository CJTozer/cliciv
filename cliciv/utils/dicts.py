def dict_apply_delta(base_dict, delta_dict):
    for key, delta in delta_dict.items():
        if key not in base_dict:
            base_dict[key] = delta
        else:
            if isinstance(delta, dict):
                dict_apply_delta(base_dict[key], delta)
            else:
                base_dict[key] += delta
