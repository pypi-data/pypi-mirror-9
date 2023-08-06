"""
Common methods shared by more than one module in this package.
"""


def check_not_blank(value, message=None):
    """
    Checks whether or not the specified `value` is blank (None or whitespace). If it is, this method
    raises a `ValueError` with the specified `message`.

    :param value: value to check
    :type value: str
    :param message: message to pass to ValueError
    :type message: str
    :raises ValueError
    """
    message = message if message else "Values must not be blank"
    value = value.strip() if value else None
    if not value:
        raise ValueError(message)

