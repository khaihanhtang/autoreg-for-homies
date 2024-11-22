from .reservation import Reservation
from ..exception.error_maker import ErrorMaker
from ..term import Term


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

    @players.setter
    def players(self, new_players: list[str]):
        self._players = new_players

    @property
    def reservations(self) -> list[Reservation]:
        return self._reservations

    @reservations.setter
    def reservations(self, new_reservations: list[Reservation]):
        self._reservations = new_reservations

    def pop_first_playable_player(self) -> Reservation:
        for i, reservation in enumerate(self._reservations):
            if reservation is not None and reservation.is_playable:
                return self._reservations.pop(i)
        raise ErrorMaker.make_pending_player_not_found_exception()

    def move_all_playable_players(self):
        while len(self._players) < self._max_num_players:
            try:
                reservation = self.pop_first_playable_player()
                if reservation is None:
                    break
                self._players.append(reservation.name)
            finally:
                break

    def is_in_players(self, proposed_name: str) -> bool:
        for name in self._players:
            if proposed_name == name:
                return True
        return False

    def is_in_reservations(self, proposed_name: str) -> bool:
        for reservation in self._reservations:
            if proposed_name == reservation.name:
                return True
        return False

    def get_reservation(self, proposed_name: str) -> Reservation or None:
        for reservation in self._reservations:
            if proposed_name == reservation.name:
                return reservation
        return None

    def is_in_any_list(self, proposed_name: str) -> bool:
        for name in self._players:
            if proposed_name == name:
                return True
        for reservation in self._reservations:
            if proposed_name == reservation.name:
                return True
        return False

    def pop_unplayable_player_from_reservations(self, proposed_name: str) -> Reservation or None:
        for i, reservation in enumerate(self._reservations):
            if proposed_name == reservation.name:
                if reservation.is_playable:
                    return None
                else:
                    return self._reservations.pop(i)
        return None

    def register(self, proposed_name: str):
        # Potentially moving from reservations to main players
        if len(self._players) < self._max_num_players:
            reservation = self.pop_unplayable_player_from_reservations(proposed_name=proposed_name)
            if reservation is not None:
                self.register(proposed_name=proposed_name)
                return

        # Changing status in reservations
        for reservation in self._reservations:
            if reservation.name == proposed_name:
                if not reservation.is_playable:
                    reservation.is_playable = True
                    return
                raise ErrorMaker.make_name_conflict_exception(message=proposed_name)

        # Otherwise, prioritize to append to main list. If not then append to reservations
        if self.is_in_any_list(proposed_name=proposed_name):
            raise ErrorMaker.make_name_conflict_exception(message=proposed_name)
        if len(self._players) < self._max_num_players:
            self._players.append(proposed_name)
        else:
            self._reservations.append(Reservation(name=proposed_name, is_playable=True))

    def pop_player_from_players(self, proposed_name: str) -> str or None:
        for i, name in enumerate(self._players):
            if name == proposed_name:
                return self._players.pop(i)
        return None

    def reserve(self, proposed_name: str, is_playable: bool):
        # if proposed_name is already in list of reservations
        for reservation in self._reservations:
            if reservation.name == proposed_name:
                if reservation.is_playable:
                    reservation.is_playable = False
                    return
                raise ErrorMaker.make_name_conflict_exception(message=proposed_name)

        # if proposed_name is in the list of players
        player_name: str = self.pop_player_from_players(proposed_name=proposed_name)
        if player_name is not None:
            self._reservations.insert(0, Reservation(name=player_name, is_playable=False))
            return
        # if proposed_name is not in anywhere
        if self.is_in_any_list(proposed_name=proposed_name):
            raise ErrorMaker.make_name_conflict_exception(message=proposed_name)
        self._reservations.append(Reservation(name=proposed_name, is_playable=is_playable))

    def deregister(self, proposed_name: str):
        if not self.is_in_any_list(proposed_name=proposed_name):
            raise ErrorMaker.make_name_not_found_exception(message=proposed_name)

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

    def to_string(self, slot_label: str) -> str:
        res = f"[{slot_label}] {self._slot_name}, {Term.NUM_PLAYERS} {self._max_num_players}\n"
        for i in range(self._max_num_players):
            res += f"{Term.INDENT_SPACE}{i + 1}."
            if i < len(self._players) and self._players[i] is not None:
                res += f" {self._players[i]}"
            res += "\n"
        for reservation in self._reservations:
            res += f"{Term.INDENT_SPACE}{Term.RESERVATION}. {reservation.name}"
            if reservation.is_playable:
                res += f" {Term.PLAYABLE}"
            res += "\n"
        return res

    def get_num_available(self) -> int:
        return self._max_num_players - len(self._players)
