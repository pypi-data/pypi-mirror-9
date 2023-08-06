from suds.sudsobject import asdict


def to_dict(obj):
    """
    Converts a suds response object to a python dict.
    :param obj: The suds object.
    :return: The object converted to a dict.
    """

    def recursive_asdict(obj):
        out = {}
        for key, val in asdict(obj).items():
            if hasattr(val, '__keylist__'):
                out[key] = recursive_asdict(val)
            elif isinstance(val, list):
                out[key] = []
                for item in val:
                    if hasattr(item, '__keylist__'):
                        out[key].append(recursive_asdict(item))
                    else:
                        out[key].append(item)
            else:
                out[key] = val

        if 'key' in out:
            out = {out['key'][0]: (out['value'][0] if len(out['value']) > 0 else '')}

        return out

    out = recursive_asdict(obj)['item']

    if len(out) == 1:
        out = out[0]
    else:
        new_dict = {}
        for elem in out:
            if not isinstance(elem, dict):
                new_dict = None
                break
            for key, val in elem.items():
                new_dict[key] = val
        if new_dict:
            out = new_dict

    return out
