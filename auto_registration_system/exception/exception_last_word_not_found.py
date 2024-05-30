class LastWordNotFoundException(Exception):

    def __init__(self):
        self._message: str = "Last word not found!"

    @property
    def message(self):
        return self._message
