import string


class DateVenueNotFoundException(Exception):
    def __init__(self):
        self.message: string = "Date not found!"