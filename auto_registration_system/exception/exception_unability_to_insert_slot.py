import string


class UnabilityToInsertSlotException(Exception):
    def __init__(self):
        self._message: string = "Unable to insert slot!"

    @property
    def message(self):
        return self._message
