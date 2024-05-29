import string


class NameNotFoundException:

    def __init__(self):
        self._message: string = "Name not found!"

    @property
    def message(self):
        return self._message
