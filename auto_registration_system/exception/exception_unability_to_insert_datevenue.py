class UnabilityToInsertDateVenueException(Exception):
    def __init__(self):
        self._message: str = "Unable to insert date!"

    @property
    def message(self):
        return self._message
