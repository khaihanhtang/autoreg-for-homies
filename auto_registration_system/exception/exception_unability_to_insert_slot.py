class UnabilityToInsertSlotException(Exception):
    def __init__(self):
        self._message: str = "Unable to insert slot!"

    @property
    def message(self):
        return self._message
