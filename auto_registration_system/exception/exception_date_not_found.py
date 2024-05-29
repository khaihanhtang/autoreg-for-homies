import string


class DateNotFoundException(Exception):
    def __init__(self):
        self.message: string = "Date not found!"