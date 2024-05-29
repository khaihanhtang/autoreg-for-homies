import string
from ..exception.exception_unability_to_insert_datevenue import UnabilityToInsertDateVenueException
from ..exception.exception_datevenue_not_found import DateVenueNotFoundException
from ..exception.exception_unability_to_insert_slot import UnabilityToInsertSlotException
from .slot_manager import SlotManager


class RegistrationData:
    def __init__(self):
        self._bookings_by_datevenue: dict = {}

    @property
    def bookings_by_datevenue(self):
        return self._bookings_by_datevenue

    def insert_datevenue(self, datevenue_name: string):
        if datevenue_name in self._bookings_by_datevenue:
            raise UnabilityToInsertDateVenueException
        self._bookings_by_datevenue[datevenue_name]: dict = {}

    def insert_slot(self, datevenue: string, slot_label: string, slot_name: string, max_num_players: int):
        if datevenue not in self._bookings_by_datevenue:
            raise DateVenueNotFoundException
        for datevenue in self._bookings_by_datevenue:
            if slot_label in self._bookings_by_datevenue[datevenue]:
                raise UnabilityToInsertSlotException
        self._bookings_by_datevenue[datevenue][slot_label]: SlotManager = SlotManager(
            slot_name=slot_name, max_num_players=max_num_players
        )
