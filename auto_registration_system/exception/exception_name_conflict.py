import string


class NameConflictException(Exception):

    def __init__(self):
        self._message: string = "Name conflict!"

    @property
    def message(self):
        return self._message
