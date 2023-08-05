# -*- coding: utf-8 -*-

class RowDataMalformed(Exception):

    """
    This exception should be trown if the data that is supposed to get into
    the database has failed for not being the correct data.

    Example:
        Input expects string but gets integer instead.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class FallOutOfRow(Exception):

    """
    This exception should be trown if the data that is supposed to get into
    the database has failed for not being the correct data.

    Example:
        Input expects string but gets integer instead.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RecordAlreadyExists(Exception):

    """
    This exception should be trown if the data that is supposed to get into
    the database has failed for not being the correct data.

    Example:
        Input expects string but gets integer instead.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
