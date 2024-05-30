class AdminRequirementException(Exception):

    def __init__(self):
        self._message: str = "You are not admin"

    @property
    def message(self):
        return self._message