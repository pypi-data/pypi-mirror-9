class Error(Exception):
    """
    Base class for exceptions in this module.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidVersionError(Error):
    """
    Raised exception in case invalid version supplied
    """
    pass


class InvalidStatusError(Error):
    """
    Raised exception in case invalid version supplied
    """
    pass


class MissingDataError(Error):
    """
    Raised exception in case invalid version supplied
    """
    pass
