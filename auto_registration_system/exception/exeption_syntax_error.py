import string


class SyntaxErrorException(Exception):

    def __init__(self, message: string):
        self._message = f"Syntax error with '{message}'"

    @property
    def message(self):
        return self._message
