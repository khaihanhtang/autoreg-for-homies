from ..exception.error_maker import ErrorMaker
from .slot_manager import SlotManager


class RegistrationData:
    def __init__(self):
        self._bookings_by_date_venue: dict[str, dict[str, SlotManager]] = dict()

    @property
    def bookings_by_date_venue(self):
        return self._bookings_by_date_venue

    def reset(self):
        self._bookings_by_date_venue = dict()

    def insert_date_venue(self, date_venue: str):
        if date_venue in self._bookings_by_date_venue:
            raise ErrorMaker.make_dv_conflict_exception(message=date_venue)
        self._bookings_by_date_venue[date_venue]: dict = {}

    def insert_slot(self, date_venue: str, slot_label: str, slot_name: str, num_players: int):
        if date_venue not in self._bookings_by_date_venue:
            raise ErrorMaker.make_dv_not_found_exception(message=date_venue)
        if slot_label in self._bookings_by_date_venue[date_venue]:
            raise ErrorMaker.make_slot_conflict_exception(message=slot_label)
        self._bookings_by_date_venue[date_venue][slot_label]: SlotManager = SlotManager(
            slot_name=slot_name, num_players=num_players
        )

    def get_slot(self, slot_label) -> SlotManager or None:
        for date_venue in self._bookings_by_date_venue:
            if slot_label in self._bookings_by_date_venue[date_venue]:
                return self._bookings_by_date_venue[date_venue][slot_label]
        return None

    def register_player(self, slot_label: str, player: str):
        slot = self.get_slot(slot_label=slot_label)
        if slot is not None:
            slot.register(proposed_name=player)
            return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def reserve_player(self, slot_label: str, player: str, is_pending: bool = False):
        slot = self.get_slot(slot_label=slot_label)
        if slot is not None:
            slot.reserve(
                proposed_name=player,
                is_pending=is_pending
            )
            return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    # def deregister_player(self, slot_label: str, player: str):
    #     slot = self.get_slot(slot_label=slot_label)
    #     if slot is not None:
    #         slot.deregister(proposed_name=player)
    #         return
    #     raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def restructure(self):
        for date_venue in self._bookings_by_date_venue:
            for slot_label in self._bookings_by_date_venue[date_venue]:
                self._bookings_by_date_venue[date_venue][slot_label].restructure()

    def collect_slot_labels_involving_user(self, id_string: str) -> list[str]:
        res: list[str] = list()
        for date_venue in self._bookings_by_date_venue:
            for slot_label, slot in self._bookings_by_date_venue[date_venue].items():
                if slot.is_in_any_list(proposed_name=id_string):
                    res.append(slot_label)
        return res

    def collect_all_slots_with_labels(self) -> list[(str, SlotManager)]:
        res: list[(str, SlotManager)] = list()
        for date_venue in self._bookings_by_date_venue:
            for slot_label, slot in self._bookings_by_date_venue[date_venue].items():
                res.append((slot_label, slot))
        return res
