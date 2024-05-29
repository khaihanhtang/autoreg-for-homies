import string


class LastWordNotFoundException(Exception):

    def __init__(self):
        self.message: string = "Last word not found!"