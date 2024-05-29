import string


class FirstWordNotFoundException(Exception):

    def __init__(self):
        self._message: string = "First word not found!"

    @property
    def message(self):
        return self._message
