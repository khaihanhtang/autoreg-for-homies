import string
from ..exception.exception_unability_to_insert_datevenue import UnabilityToInsertDateVenueException
from ..exception.exception_datevenue_not_found import DateVenueNotFoundException
from ..exception.exception_unability_to_insert_slot import UnabilityToInsertSlotException
from slot_manager import SlotManager


class RegistrationData:
    def __init__(self):
        self.bookings_by_datevenue: dict = {}

    def insert_datevenue(self, datevenue_name: string):
        if datevenue_name in self.bookings_by_datevenue:
            raise UnabilityToInsertDateVenueException
        self.bookings_by_datevenue[datevenue_name]: dict = {}

    def insert_slot(self, datevenue_name: string, slot_name: string, max_num_players: int):
        if datevenue_name not in self.bookings_by_datevenue:
            raise DateVenueNotFoundException
        for datevenue in self.bookings_by_datevenue:
            if slot_name in self.bookings_by_datevenue[datevenue]:
                raise UnabilityToInsertSlotException
        self.bookings_by_datevenue[datevenue_name][slot_name]: SlotManager = SlotManager(max_num_players=max_num_players)
