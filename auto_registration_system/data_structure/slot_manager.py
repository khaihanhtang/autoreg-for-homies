from .reservation import Reservation
from ..exception.exception_name_conflict import NameConflictException
from ..exception.exception_name_not_found import NameNotFoundException


class SlotManager:

    def __init__(self, slot_name: str, max_num_players: int):
        self._slot_name: str = slot_name
        self._max_num_players: int = max_num_players
        self._players: list[str] = []
        self._reservations: list[Reservation] = []

    @property
    def slot_name(self) -> str:
        return self._slot_name

    @property
    def max_num_players(self) -> int:
        return self._max_num_players

    @property
    def players(self) -> list[str]:
        return self._players

    @property
    def reservations(self) -> list[Reservation]:
        return self._reservations

    def pop_first_playable_player(self) -> Reservation:
        for i, reservation in enumerate(self._reservations):
            if reservation is not None and reservation.is_playable:
                return self._reservations.pop(i)
        raise Exception("No playable player!")

    def move_all_playable_players(self):
        while len(self._players) < self._max_num_players:
            try:
                reservation = self.pop_first_playable_player()
                if reservation is None:
                    break
                self._players.append(reservation.name)
            except Exception as e:
                break

    def is_in_any_list(self, proposed_name: str) -> bool:
        for name in self._players:
            if proposed_name == name:
                return True
        for reservation in self._reservations:
            if proposed_name == reservation.name:
                return True
        return False

    def insert(self, proposed_name: str):
        if self.is_in_any_list(proposed_name=proposed_name):
            raise NameConflictException
        if len(self._players) < self._max_num_players:
            self._players.append(proposed_name)
        else:
            self._reservations.append(Reservation(name=proposed_name, is_playable=True))

    def insert_reservation(self, proposed_name: str, is_playable: bool):
        if self.is_in_any_list(proposed_name=proposed_name):
            raise NameConflictException
        self._reservations.append(Reservation(name=proposed_name, is_playable=is_playable))

    def remove(self, proposed_name: str):
        if not self.is_in_any_list(proposed_name=proposed_name):
            raise NameNotFoundException

        if proposed_name in self._players:
            self._players.remove(proposed_name)
            self.move_all_playable_players()
            new_list = []
            for name in self._players:
                if name is not None:
                    new_list.append(name)
            self._players = new_list
        else:
            for i, reservation in enumerate(self._reservations):
                if reservation.name == proposed_name:
                    self._reservations.pop(i)
