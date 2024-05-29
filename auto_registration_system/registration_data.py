import string
from exception.exception_unability_to_insert_date import UnabilityToInsertDateException
from exception.exception_date_not_found import DateNotFoundException
from exception.exception_unability_to_insert_slot import UnabilityToInsertSlotException


class RegistrationData:
    def __init__(self):
        self.bookings_by_date: dict = {}

    def insert_date(self, date_name: string):
        if date_name in self.bookings_by_date:
            raise UnabilityToInsertDateException
        self.bookings_by_date[date_name]: dict = {}

    def insert_slot(self, date_name: string, slot_name: string):
        if date_name not in self.bookings_by_date:
            raise DateNotFoundException
        if slot_name in self.bookings_by_date[date_name]:
            raise UnabilityToInsertSlotException
        self.bookings_by_date[date_name][slot_name]: list = []
