import string

class AdminRequirementException(Exception):

    def __init__(self):
        self.message: string = "You are not admin"

