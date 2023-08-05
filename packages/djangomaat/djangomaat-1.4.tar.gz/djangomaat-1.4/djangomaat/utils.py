def auto_increment(start_value=0):
    """Returns an iterator over an auto increment value."""
    value = start_value - 1
    while True:
        value += 1
        yield value
