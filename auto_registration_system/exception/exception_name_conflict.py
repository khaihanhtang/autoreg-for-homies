class NameConflictException(Exception):

    def __init__(self):
        self._message: str = "Name conflict!"

    @property
    def message(self):
        return self._message
