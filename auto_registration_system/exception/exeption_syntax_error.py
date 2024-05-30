class SyntaxErrorException(Exception):

    def __init__(self, message: str):
        self._message = f"Syntax error with '{message}'"

    @property
    def message(self):
        return self._message
