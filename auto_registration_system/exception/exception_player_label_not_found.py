class PlayerLabelNotFoundException(Exception):

    def __init__(self):
        self._message: str = "Player label not found!"

    @property
    def message(self):
        return self._message
