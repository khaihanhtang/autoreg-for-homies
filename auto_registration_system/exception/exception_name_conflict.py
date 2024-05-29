import string


class NameConflictException(Exception):

    def __init__(self):
        self.message: string = "Name conflict!"