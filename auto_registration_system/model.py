from typing import Optional


class SlotDetail:
    """Represent the details of a slot, including its name, number of players,
    and owner (if any)."""

    def __init__(self, slot_label: str, date_venue: str, time: str, court: str, num_players: int, owner: Optional[str] = None):
        self.slot_label = slot_label
        self.date_venue = date_venue
        self.time = time
        self.court = court
        self.num_players = num_players
        self.owner = owner
      

class User:
    """Represent a user from telegram with username & an optional alias"""
    def __init__(self, username: str, alias: Optional[str], is_admin: bool = False):
        self.username = username
        self.alias = alias
        self.is_admin = is_admin


class Player:
    """Represent a registered player with name, payment status, and whether they are a reserve"""
    def __init__(self,
                 name: str,
                 is_paid: bool = False,
                 is_pending: bool = False,
                 is_reserve: bool = False):
        self.name = name
        self.is_paid = is_paid
        self.is_pending = is_pending
        self.is_reserve = is_reserve
