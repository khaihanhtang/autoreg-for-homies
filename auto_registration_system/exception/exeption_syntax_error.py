import string


class SyntaxErrorException(Exception):

    def __init__(self, message: string):
        self.message = f"Syntax error with '{message}'"