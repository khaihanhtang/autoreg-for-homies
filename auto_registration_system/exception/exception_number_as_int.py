class NumberAsIntException(Exception):

    def __init__(self):
        self._message = "Number error!"

    @property
    def message(self):
        return self._message
