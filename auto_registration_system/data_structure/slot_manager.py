import string
from ..exception.exception_name_conflict import NameConflictException
from ..exception.exception_name_not_found import NameNotFoundException


class SlotManager:

    def __init__(self, max_num_players: int):
        self.max_num_players: int = max_num_players
        self.players = []
        self.reservations = []

    def is_in_any_list(self, proposed_name: string) -> bool:
        for name in self.players:
            if proposed_name == name:
                return True
        for name in self.reservations:
            if proposed_name == name:
                return True
        return False

    def insert(self, proposed_name: string):
        if self.is_in_any_list(proposed_name=proposed_name):
            raise NameConflictException
        if len(self.players) < self.max_num_players:
            self.players.append(proposed_name)
        else:
            self.reservations.append(proposed_name)

    def insert_reservation(self, proposed_name: string):
        if self.is_in_any_list(proposed_name=proposed_name):
            raise NameConflictException
        self.reservations.append(proposed_name)

    def remove(self, proposed_name: string):
        if not self.is_in_any_list(proposed_name=proposed_name):
            raise NameNotFoundException

        if proposed_name in self.players:
            self.players.remove(proposed_name)
            moved_name = None
            if len(self.reservations) > 0:  # move member from reservations to players if any
                moved_name = self.reservations.pop(0)
            self.players.append(moved_name)
        else:
            self.reservations.remove(proposed_name)
