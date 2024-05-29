import string


class DateVenueNotFoundException(Exception):
    def __init__(self):
        self._message: string = "Date/Venue not found!"

    @property
    def message(self):
        return self._message
