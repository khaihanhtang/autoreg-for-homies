class SlotLabelNotFoundException(Exception):

    def __init__(self):
        self._message: str = "Slot label not found!"

    @property
    def message(self):
        return self._message
