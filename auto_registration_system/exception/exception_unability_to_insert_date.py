import string


class UnabilityToInsertDateException(Exception):
    def __init__(self):
        self.message: string = "Unable to insert date!"