import string


class UnabilityToInsertSlotException(Exception):
    def __init__(self):
        self.message: string = "Unable to insert slot!"