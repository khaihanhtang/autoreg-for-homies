from ..exception.error_maker import ErrorMaker
from ..exception.exception_slot_label_not_found import SlotLabelNotFoundException
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

    def insert_datevenue(self, datevenue_name: str):
        if datevenue_name in self._bookings_by_datevenue:
            raise ErrorMaker.make_dv_conflict_exception(message=datevenue_name)
        self._bookings_by_datevenue[datevenue_name]: dict = {}

    def insert_slot(self, datevenue: str, slot_label: str, slot_name: str, max_num_players: int):
        if datevenue not in self._bookings_by_datevenue:
            raise ErrorMaker.make_dv_not_found_exception(message=datevenue)
        for datevenue in self._bookings_by_datevenue:
            if slot_label in self._bookings_by_datevenue[datevenue]:
                raise ErrorMaker.make_slot_conflict_exception(message=slot_label)
        self._bookings_by_datevenue[datevenue][slot_label]: SlotManager = SlotManager(
            slot_name=slot_name, max_num_players=max_num_players
        )

    def insert_player(self, slot_label: str, player: str):
        for datevenue in self._bookings_by_datevenue:
            if slot_label in self._bookings_by_datevenue[datevenue]:
                self._bookings_by_datevenue[datevenue][slot_label].insert(proposed_name=player)
                return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def insert_reservation(self, slot_label: str, player: str, is_playable: bool = False):
        for datevenue in self._bookings_by_datevenue:
            if slot_label in self._bookings_by_datevenue[datevenue]:
                self._bookings_by_datevenue[datevenue][slot_label].insert_reservation(
                    proposed_name=player,
                    is_playable=is_playable
                )
                return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def remove(self, slot_label: str, player: str):
        for datevenue in self._bookings_by_datevenue:
            if slot_label in self._bookings_by_datevenue[datevenue]:
                self._bookings_by_datevenue[datevenue][slot_label].remove(proposed_name=player)
                return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def move_all_playable_players(self):
        for datevenue in self._bookings_by_datevenue:
            for slot_label in self._bookings_by_datevenue[datevenue]:
                self._bookings_by_datevenue[datevenue][slot_label].move_all_playable_players()