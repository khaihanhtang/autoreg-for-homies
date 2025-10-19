from typing import Optional

from ..exception.error_maker import ErrorMaker
from .slot_manager import SlotManager
from auto_registration_system.model import SlotDetail


class RegistrationData:
    def __init__(self):
        self._bookings_by_date_venue: dict[str, dict[str, SlotManager]] = dict()

    @property
    def bookings_by_date_venue(self):
        return self._bookings_by_date_venue

    def reset(self):
        self._bookings_by_date_venue = dict()

    def insert_slot_detail(self, slot_detail: SlotDetail):
        """Insert a slot detail into the registration data structure.
        This method combines insert_date_venue and insert_slot for convenience."""
        date_venue = slot_detail.date_venue
        slot_label = slot_detail.slot_label
        num_players = slot_detail.num_players
        owner = slot_detail.owner

        # TODO: inverse the index so that we can find the slot detail by label directly

        if date_venue not in self._bookings_by_date_venue:
            self._bookings_by_date_venue[date_venue] = {}

        if slot_label in self._bookings_by_date_venue[date_venue]:
            raise ErrorMaker.make_slot_conflict_exception(message=slot_label)

        self._bookings_by_date_venue[date_venue][slot_label] = SlotManager(
            slot_name=slot_label, num_players=num_players, owner=owner
        )


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

    def get_slot(self, slot_label) -> Optional[SlotManager]:
        """Return the slot with the given label, or None if not found."""
        for date_venue in self._bookings_by_date_venue:
            if slot_label in self._bookings_by_date_venue[date_venue]:
                return self._bookings_by_date_venue[date_venue][slot_label]
        return None

    def register_player(self, slot_label: str, player: str):
        """Register a player to the slot with the given label.
        If the slot is already full, player will be added to the reserve list.
        If the slot is not found, raise an exception."""
        slot = self.get_slot(slot_label=slot_label)
        if slot is not None:
            slot.register(proposed_name=player)
            return
        raise ErrorMaker.make_slot_not_found_exception(message=slot_label)

    def reserve_player(self, slot_label: str, player: str):
        slot = self.get_slot(slot_label=slot_label)
        if slot is not None:
            slot.reserve(proposed_name=player)
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

    #FIXME: unused
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
