def Bool(x):
    """ Converts the value into a boolean representation. """
    try:
        y = bool(int(x))
    except (ValueError, TypeError):
        y = bool(x)
    return y