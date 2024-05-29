import string


class FirstWordNotFoundException(Exception):

    def __init__(self):
        self.message: string = "First word not found!"