import json


# helpers
def _build_simple_property(values):
    return values[0]


def _rstrip(in_list, value=None):
    l, n = list(in_list), list()
    while l and l[-1] is None:
        n.append(l.pop(-1))
    return l


def _build_subtable(values):
    striped_values = [_rstrip(l) for l in values if _rstrip(l)]
    if striped_values:
        m = max(len(l) for l in striped_values)
        line = [l[:m] for l in values]
        return line


# converter
def dict_from_range(range_list):
    # separate keys and values
    key_list = list()
    value_list = list()
    for line in range_list:
        key, value = line[0], line[1:]
        if not key and all(n is None for n in value):
            # drop empty lines
            continue
        # if no key given take previous one
        key = key if key else key_list[-1]
        key_list.append(key)
        value_list.append(value)

    # collect all into a dict
    key_value_dict = dict()
    for key, value in zip(key_list, value_list):
        if all(v is None for v in value):
            # key but no values indicates new multi line value
            key_value_dict[key] = list()
        elif key in key_value_dict:
            # key exists, must be a multi line value
            key_value_dict[key].append(value)
        else:
            # key doesn't exists, must be a single line value
            key_value_dict[key] = value

    # strip values
    for key, value in key_value_dict.iteritems():
        # could be : a) list -> simple property or b) nested list -> range property
        if value:
            if isinstance(value[0], (list, tuple)):
                value = _build_subtable(value)
            else:
                value = _build_simple_property(value)
            key_value_dict[key] = value

    return key_value_dict


def range_from_dict(range_dict, key_order=()):
    rng_dict = dict(range_dict)
    # first build flattering range
    rng = list()
    for key in list(key_order)+sorted(rng_dict.keys()):
        if key in rng_dict:
            value = rng_dict.pop(key)
            if isinstance(value, (list, tuple)):
                rng.append([key])
                for v in value:
                    rng.append(list([None] + v))
            else:
                rng.append([key, value])

    # set each line in range to same length
    lng = max(len(l) for l in rng)
    for i in range(len(rng)):
        rng[i] = list(rng[i] + [None] * (lng - len(rng[i])))

    return rng


def json_from_range(rng_list, **kwargs):
    rng_dict = dict_from_range(rng_list)
    return json.dumps(rng_dict, **kwargs)


def range_from_json(json_str, **kwargs):
    rng_dict = json.loads(json_str, **kwargs)
    return range_from_dict(rng_dict)


def csv_from_range(rng_list, **kwargs):
    pass


def range_from_csv(csv_str, **kwargs):
    pass
