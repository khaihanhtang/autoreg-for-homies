from ..exception.error_maker import ErrorMaker
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

    def get_slot(self, slot_label) -> SlotManager or None:
        for datevenue in self._bookings_by_datevenue:
            if slot_label in self._bookings_by_datevenue[datevenue]:
                return self._bookings_by_datevenue[datevenue][slot_label]
        return None

    def register_player(self, slot_label: str, player: str):
        slot = self.get_slot(slot_label=slot_label)
        if slot is not None:
            slot.register(proposed_name=player)
            return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def reserve_player(self, slot_label: str, player: str, is_playable: bool = False):
        slot = self.get_slot(slot_label=slot_label)
        if slot is not None:
            slot.reserve(
                proposed_name=player,
                is_playable=is_playable
            )
            return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def deregister_player(self, slot_label: str, player: str):
        slot = self.get_slot(slot_label=slot_label)
        if slot is not None:
            slot.deregister(proposed_name=player)
            return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def move_all_playable_players(self):
        for date_venue in self._bookings_by_datevenue:
            for slot_label in self._bookings_by_datevenue[date_venue]:
                self._bookings_by_datevenue[date_venue][slot_label].move_all_playable_players()

    def collect_slot_labels_involving_user(self, full_name: str) -> list[str]:
        res: list[str] = list()
        for date_venue in self._bookings_by_datevenue:
            for slot_label, slot in self._bookings_by_datevenue[date_venue].items():
                if slot.is_in_any_list(proposed_name=full_name):
                    res.append(slot_label)
        return res
