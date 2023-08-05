import copy


def dictmerge(target, source, *sources):
    """
    Recursively merge `targets` into `source`.
    """
    if sources:
        dictmerge(target, source)
        for source in sources:
            dictmerge(target, source)
    else:
        if not isinstance(source, dict):
            return source
        for k, v in source.iteritems():
            if k in target and isinstance(target[k], dict):
                dictmerge(target[k], v)
            else:
                target[k] = copy.deepcopy(v)
    return target
