import string


class UnabilityToInsertDateVenueException(Exception):
    def __init__(self):
        self.message: string = "Unable to insert date!"