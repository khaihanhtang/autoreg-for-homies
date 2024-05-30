class DateVenueNotFoundException(Exception):
    def __init__(self):
        self._message: str = "Date/Venue not found!"

    @property
    def message(self):
        return self._message
