def convert(dict, key, type):
    if key in dict:
        dict[key] = type(dict[key])


def parse_bool(value):
    """Semi-blind boolean conversion that treats "False" and u"False"
    as False, not True. If fed a boolean, nothing happens and the
    value is returned as-is.
    
        >>> parse_bool("False")
        False
        >>> parse_bool("True")
        True
        >>> parse_bool(False)
        False
        >>> parse_bool(True)
        True
    """
    return bool({
        'True': True,
        'False': False
    }.get(value, value))
