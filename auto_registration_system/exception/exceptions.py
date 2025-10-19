class ActionNotAllowedException(Exception):

    def __init__(self, message):
        self._message: str = message
