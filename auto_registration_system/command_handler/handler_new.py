import re
from typing import Optional

from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.model import SlotDetail, Player, User
from string_parser.string_parser import StringParser
from ..exception.error_maker import ErrorMaker
from ..term import Term


class NewHandler:

    @staticmethod
    def is_date_venue_line(message: str) -> bool:
        try:
            first_word: str = StringParser.get_first_word(message=message)
        except Exception:
            return False
        if first_word in {Term.DATE_VENUE, Term.DATE_VENUE_SHORTENED}:
            return True
        return False

    @staticmethod
    def get_slot_label(message: str) -> str:
        first_word: str = StringParser.get_first_word(message=message)
        tag = first_word
        if first_word[0] == "[" and first_word[-1:] == "]":
            if len(first_word) >= 3:
                tag = first_word[1:-1]
            else:
                tag = ""
        try:
            if not (tag.islower() and tag.isalnum()):
                raise ErrorMaker.make_syntax_error_exception(message=message)
            return tag
        except Exception:
            raise ErrorMaker.make_syntax_error_exception(message=message)

    @staticmethod
    def is_slot_line(message: str) -> bool:
        try:
            NewHandler.get_slot_label(message=message)
            return True
        except Exception:
            return False

    @staticmethod
    def get_player_label(message: str) -> str:
        first_word: str = StringParser.get_first_word(message=message)
        try:
            if not (first_word[-1:] == "." and len(first_word) >= 2):
                raise ErrorMaker.make_syntax_error_exception(message=message)
            return first_word[:-1]
        except Exception:
            raise ErrorMaker.make_syntax_error_exception(message=message)

    @staticmethod
    def is_player_line(message: str) -> bool:
        try:
            NewHandler.get_player_label(message=message)
            return True
        except Exception:
            return False

    @staticmethod
    def handle(user: User, message: str, data: RegistrationData, max_num_players: int) -> bool:
        message = StringParser.remove_command(message=message)

        # parsing state - update this as we parse the header
        current_date_venue: str or None = None
        current_slot_label: str or None = None

        count_processed: int = 0
        for line in message.splitlines():
            current_message = line.strip()
            if not current_message:
                continue

            count_processed += 1
            if NewHandler.is_date_venue_line(message=current_message):
                current_date_venue = NewHandler.parse_date_venue_line(current_message)
                current_slot_label = None
                
            elif NewHandler.is_slot_line(message=current_message):
                slot_detail: SlotDetail = NewHandler.parse_slot_line(line=current_message)
                slot_detail.date_venue = current_date_venue

                # validations
                if slot_detail.num_players is None:
                    slot_detail.num_players = max_num_players
                if slot_detail.num_players > max_num_players:
                    raise ErrorMaker.make_num_players_exceeding_maximum_allowed_exception(
                        message=current_message,
                        max_num_players=max_num_players
                    )

                data.insert_slot_detail(slot_detail=slot_detail)
                # update this address for subsequent player lines
                current_slot_label = slot_detail.slot_label

            elif NewHandler.is_player_line(message=current_message):
                player = NewHandler.parse_player_line(current_message)
                if player is None:
                    continue
                if current_date_venue is None:
                    raise ErrorMaker.make_dv_not_found_exception(message=line)
                if current_slot_label is None:
                    raise ErrorMaker.make_slot_not_found_exception(message=line)

                if player.is_reserve and not player.is_pending:
                    data.reserve_player(current_slot_label, player.name.title())
                else:
                    data.register_player(current_slot_label, player.name.title())
                
                if player.is_paid:
                    data.get_slot(current_slot_label).confirm_payment(player.name, user)
            else:
                if len(current_message) > 0:
                    raise ErrorMaker.make_syntax_error_exception(message=line)
                count_processed -= 1
        if count_processed == 0:
            return False

        return True

    @staticmethod
    def parse_date_venue_line(line: str) -> str:
        """Parse a line defining a date and venue and return the date_venue string."""
        # line to parse looks something like below
        # [dv] 🏸14/09 SUN Queenstown cc
        line = line.strip()
        if line.startswith(Term.DATE_VENUE):
            return line[len(Term.DATE_VENUE):].strip()
        if line.startswith(Term.DATE_VENUE_SHORTENED):
            return line[len(Term.DATE_VENUE_SHORTENED):].strip()

        raise ErrorMaker.make_syntax_error_exception(message=line, hint="Line must start with [dv] or dv")

    @staticmethod
    def parse_slot_line(line: str) -> SlotDetail:
        """Parse a line defining a slot and return a SlotDetail object."""

        # line to parse looks something like below
        # [s] ❤️1:00-3:00 pm (1), #players: 7
        # or
        # [s] ❤️1:00-3:00 pm (1), #players: 7, #owner: @alice
        print(f"Parsing slot line: '{line}'")

        slot_label = ""
        time: Optional[str] = None
        num_players: Optional[int] = None
        owner: Optional[str] = None

        for idx, part in enumerate(line.strip().split(",")):
            if len(part) == 0:
                continue

            part = part.strip()
            if idx == 0:
                m = re.search(r"\[(.+)\](.*)", part)
                if not m:
                    raise ErrorMaker.make_syntax_error_exception(message=line, hint="Expecting slot [x]")
                slot_label = m.group(1).strip()
                time = m.group(2).strip()
                continue
            if not part:
                # skip over empty parts
                continue
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == Term.NUM_PLAYERS[:-1].lower():
                    try:
                        num_players = int(value)
                    except ValueError:
                        raise ErrorMaker.make_syntax_error_exception(message=line)
                elif key == Term.OWNER[:-1].lower():
                    if value.startswith("@"):
                        owner = value[1:].strip()
                    else:
                        owner = value.strip()
                else:
                    print(f"Unknown key '{key}' in slot line '{line}'")
                    raise ErrorMaker.make_syntax_error_exception(message=line, hint=f"Unknown key '{key}'")

        print(f"Parsed slot line: label='{slot_label}', time='{time}', num_players='{num_players}', owner='{owner}'")
        return SlotDetail(
            slot_label=slot_label,
            date_venue="",
            time=time,
            court="",
            num_players=num_players,
            owner=owner
        )

    @staticmethod
    def parse_player_line(line: str) -> Player:
        """Parse a line defining a player and return the player's name."""
        # line to parse looks something like below
        # 1. Alice (pending payment)
        # 2. Bob (paid)
        # 3. Charlie
        # 4.
        # reserve. David
        # reserve. Eve (pending)

        line = line.strip()
        begin = 0
        end = len(line)

        label = ""
        is_pending = False
        is_reserve = False
        payment_status: Optional[str] = None

        # consume "reserve"
        if line.startswith(Term.RESERVATION):
            label = Term.RESERVATION
            is_reserve = True
            begin += len(Term.RESERVATION)
        # consumer whitespace and row number
        while begin < end and (line[begin].isspace() or line[begin].isdigit() or line[begin] in {".", "#"}):
            begin += 1
        label = line[:begin].strip()

        if line.endswith(Term.PAYMENT_PENDING):
            end -= len(Term.PAYMENT_PENDING)
            payment_status = Term.PAYMENT_PENDING
        elif line.endswith(Term.PAYMENT_PAID):
            end -= len(Term.PAYMENT_PAID)
            payment_status = Term.PAYMENT_PAID
        elif line.endswith(Term.PENDING):
            end -= len(Term.PENDING)
            is_pending = True
        _ = label
        
        player_name = line[begin:end].strip()
        if not player_name:
            return None

        # if not player_name:
        #     raise ErrorMaker.make_syntax_error_exception(message=line, hint="Player name cannot be empty")

        return Player(player_name, payment_status == Term.PAYMENT_PAID, is_pending, is_reserve)
