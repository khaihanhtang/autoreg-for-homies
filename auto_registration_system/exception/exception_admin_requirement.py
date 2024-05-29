import string

class AdminRequirementException(Exception):

    def __init__(self):
        self._message: string = "You are not admin"

    @property
    def message(self):
        return self._message