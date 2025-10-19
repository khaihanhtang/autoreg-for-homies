from typing import Optional

from auto_registration_system.term import Term
from auto_registration_system.exception.error_maker import ErrorMaker
from auto_registration_system.exception.exceptions import ActionNotAllowedException
from auto_registration_system.model import User


class SlotManager:

    def __init__(self, slot_name: str, num_players: int,
                 extra_cost: Optional[int] = None, owner: Optional[str] = None):
        self._slot_name: str = slot_name
        self._num_players: int = num_players
        self._players: list[str] = []
        self._pending_reservations: list[str] = []
        self._non_pending_reservations: list[str] = []
        self._extra_cost: Optional[int] = extra_cost
        self._owner: Optional[str] = owner
        self._confirmed_payments: set[str] = set()

    @property
    def slot_name(self) -> str:
        return self._slot_name

    @property
    def num_players(self) -> int:
        return self._num_players

    @property
    def owner(self) -> Optional[str]:
        return self._owner

    @property
    def players(self) -> list[str]:
        return self._players

    @players.setter
    def players(self, new_players: list[str]):
        self._players = new_players

    @property
    def pending_reservations(self) -> list[str]:
        return self._pending_reservations

    @pending_reservations.setter
    def pending_reservations(self, pending_reservation: list[str]):
        self._pending_reservations = pending_reservation

    @property
    def non_pending_reservations(self) -> list[str]:
        return self._non_pending_reservations

    @non_pending_reservations.setter
    def non_pending_reservations(self, non_pending_reservation: list[str]):
        self._non_pending_reservations = non_pending_reservation

    def _pop_first_pending_player(self) -> str or None:
        if self._pending_reservations:
            return self._pending_reservations.pop(0)
        return None

    # sorting the lists, pending players will be moved to main players if possible,
    # and pending players are placed before non-pending players
    def restructure(self):
        while len(self._players) < self._num_players:
            player = self._pop_first_pending_player()
            if player is None:
                break
            self._players.append(player)

    def is_in_any_list(self, proposed_name: str) -> bool:
        return (
                (proposed_name in self._players)
                or (proposed_name in self._pending_reservations)
                or (proposed_name in self._non_pending_reservations)
        )

    def _remove_player_from_non_pending_reservations(self, proposed_name: str) -> bool:
        found = False
        try:
            self._non_pending_reservations.remove(proposed_name)
            found = True
        except ValueError:
            pass
        return found

    def _remove_player_from_pending_reservations(self, proposed_name: str) -> bool:
        found = False
        try:
            self._pending_reservations.remove(proposed_name)
            found = True
        except ValueError:
            pass
        return found

    def _remove_player_from_players(self, proposed_name: str) -> bool:
        found = False
        try:
            self._players.remove(proposed_name)
            found = True
        except ValueError:
            pass
        return found

    def register(self, proposed_name: str):
        """Adding a user to this"""
        # Potentially moving from reservations to main players
        is_successful_popping_player = self._remove_player_from_non_pending_reservations(proposed_name=proposed_name)
        if is_successful_popping_player:
            self.register(proposed_name=proposed_name)
            return

        # prioritize to append to main list. If not then append to pending reservations
        if self.is_in_any_list(proposed_name=proposed_name):
            raise ErrorMaker.make_name_conflict_exception(message=proposed_name)

        if len(self._players) < self._num_players:
            self._players.append(proposed_name)
        else:
            self._pending_reservations.append(proposed_name)
        self.restructure()

    def is_paid_user(self, user: str) -> bool:
        """Return whether a user has paid in this slot"""
        return user in self._confirmed_payments

    # FIXME: we need to confirm payment from the file too
    # so the permission check should go up one level

    def confirm_payment(self, user: str, actioner: User) -> bool:
        """Confirm payment for a user in this slot.
        Return whether there is new successful confirmation"""
        if not self._can_confirm_payment(actioner):
            raise ActionNotAllowedException(
                f"User {actioner.username} ({actioner.alias}) cannot confirm for owner ${self._owner}"
            )

        if user in self._confirmed_payments:
            # already paid - does nothing
            # maybe return something here to tell user
            return False

        if user not in self._players:
            # user not yet registered - can't confirm
            return False

        # now actually confirming this payment
        self._confirmed_payments.add(user)
        return True

    def unconfirm_payment(self, user: str, actioner: User) -> bool:
        """Unconfirm payment for a user in this slot.
        Return whether there is new successful unconfirmation"""
        if not self._can_confirm_payment(actioner):
            raise ActionNotAllowedException(
                f"User {actioner.username} ({actioner.alias}) cannot unconfirm for owner ${self._owner}"
            )

        if user not in self._confirmed_payments:
            # already paid - does nothing
            # maybe return something here to tell user
            return False

        if user not in self._players:
            # user not yet registered - can't unconfirm
            return False

        # now actually unconfirming this payment
        self._confirmed_payments.remove(user)
        return True


    def reserve(self, proposed_name: str):
        self._remove_player_from_players(proposed_name=proposed_name)
        self._remove_player_from_pending_reservations(proposed_name=proposed_name)
        if proposed_name not in self._non_pending_reservations:
            self._non_pending_reservations.append(proposed_name)
        self.restructure()

    def to_string(self, slot_label: str) -> str:
        res = f"[{slot_label}] {self._slot_name}, {Term.NUM_PLAYERS} {self._num_players}\n"
        for i in range(self._num_players):
            res += f"{Term.INDENT_SPACE}{i + 1}."
            if i < len(self._players) and self._players[i] is not None:
                res += f" {self._format_player(self._players[i])}"
            res += "\n"
        for player in self._pending_reservations:
            res += f"{Term.INDENT_SPACE}{Term.RESERVATION}. {player}"
            res += f" {Term.PENDING}"
            res += "\n"
        for player in self._non_pending_reservations:
            res += f"{Term.INDENT_SPACE}{Term.RESERVATION}. {player}"
            # res += f" {Term.PENDING}"
            res += "\n"
        return res

    def get_num_available(self) -> int:
        return self._num_players - len(self._players)

    def _can_confirm_payment(self, user: User) -> bool:
        """Return whether a user has the permission to confirm payment for this slot"""
        return user.is_admin or user.username == self._owner or user.alias == self._owner

    def _format_player(self, player: str) -> str:
        """Format a player name with optional payment status"""
        if self._extra_cost is None:
            return player

        if player in self._confirmed_payments:
            return f"{player} (paid)"

        return f"{player} (pending payment)"
