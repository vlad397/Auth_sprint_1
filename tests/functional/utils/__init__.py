def get_cache_key(function_name: str, kwargs: dict):
    cache_key = function_name + "="
    for k, v in kwargs.items():
        cache_key += "::" + str(k) + "::" + str(v)
    return cache_key