import string
from ..exception.exception_name_conflict import NameConflictException
from ..exception.exception_name_not_found import NameNotFoundException


class SlotManager:

    def __init__(self, slot_name: string, max_num_players: int):
        self._slot_name: string = slot_name
        self._max_num_players: int = max_num_players
        self._players = []
        self._reservations = []

    @property
    def slot_name(self) -> string:
        return self._slot_name

    @property
    def max_num_players(self) -> int:
        return self._max_num_players

    @property
    def players(self) -> list[string]:
        return self._players

    @property
    def reservations(self) -> list[string]:
        return self._reservations

    def is_in_any_list(self, proposed_name: string) -> bool:
        for name in self._players:
            if proposed_name == name:
                return True
        for name in self._reservations:
            if proposed_name == name:
                return True
        return False

    def insert(self, proposed_name: string):
        if self.is_in_any_list(proposed_name=proposed_name):
            raise NameConflictException
        if len(self._players) < self._max_num_players:
            self._players.append(proposed_name)
        else:
            self._reservations.append(proposed_name)

    def insert_reservation(self, proposed_name: string):
        if self.is_in_any_list(proposed_name=proposed_name):
            raise NameConflictException
        self._reservations.append(proposed_name)

    def remove(self, proposed_name: string):
        if not self.is_in_any_list(proposed_name=proposed_name):
            raise NameNotFoundException

        if proposed_name in self._players:
            self._players.remove(proposed_name)
            moved_name = None
            if len(self._reservations) > 0:  # move member from reservations to players if any
                moved_name = self._reservations.pop(0)
            self._players.append(moved_name)
            new_list = []
            for name in self._players:
                if name is not None:
                    new_list.append(name)
            self._players = new_list
        else:
            self._reservations.remove(proposed_name)
