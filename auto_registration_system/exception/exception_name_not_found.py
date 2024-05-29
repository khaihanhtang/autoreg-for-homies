import string


class NameNotFoundException:

    def __init__(self):
        self.message: string = "Name not found!"