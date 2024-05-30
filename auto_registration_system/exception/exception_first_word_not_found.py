class FirstWordNotFoundException(Exception):

    def __init__(self):
        self._message: str = "First word not found!"

    @property
    def message(self):
        return self._message
